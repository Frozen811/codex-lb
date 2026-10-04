from __future__ import annotations

import asyncio
import json

import pytest
from websockets.asyncio.client import connect
from websockets.asyncio.server import serve

from app.core.clients.native_egress import NativeWebSocketRequest
from app.core.clients.proxy_websocket import NativeUpstreamWebSocket, WebsocketsUpstreamWebSocket
from tests.integration import test_native_sse_egress as native_sse

pytestmark = pytest.mark.integration
native_worker = native_sse.native_worker


@pytest.mark.asyncio
@pytest.mark.parametrize("adapter", ["python", "native"])
async def test_real_socket_abort_preserves_positive_transport_ending(native_worker, adapter):
    async def origin(socket):
        await socket.recv()
        await socket.send(json.dumps({"type": "response.created", "response": {"id": "resp_wire"}}))
        socket.transport.abort()

    async with serve(origin, "127.0.0.1", 0) as server:
        url = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/responses"
        upstream = (
            NativeUpstreamWebSocket(
                await native_worker.websocket(
                    NativeWebSocketRequest(
                        url=url, headers={}, connect_timeout_seconds=5, max_message_bytes=1024 * 1024
                    )
                )
            )
            if adapter == "native"
            else WebsocketsUpstreamWebSocket(await connect(url))
        )
        try:
            await upstream.send_text('{"type":"response.create"}')
            assert (await asyncio.wait_for(upstream.receive(), timeout=5)).kind == "text"
            terminal = await asyncio.wait_for(upstream.receive(), timeout=5)
            assert terminal.close_code in (None, 1006)
            assert terminal.kind == "close" or terminal.transport_ended
        finally:
            await upstream.close()
