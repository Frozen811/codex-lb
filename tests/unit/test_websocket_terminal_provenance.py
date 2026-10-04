from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import aiohttp
import pytest
from websockets.exceptions import ConnectionClosedError

from app.core.clients.native_egress import NativeEgressProtocolError, NativeEgressTransportError
from app.core.clients.proxy_websocket import (
    CodexUpstreamWebSocket,
    NativeUpstreamWebSocket,
    WebsocketsUpstreamWebSocket,
)

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_direct_incomplete_handshake_carries_positive_ending_provenance():
    connection = SimpleNamespace(recv=AsyncMock(side_effect=ConnectionClosedError(None, None)))
    message = await WebsocketsUpstreamWebSocket(connection).receive()
    assert message.kind == "error"
    assert message.close_code is None
    assert message.transport_ended


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "closed,protocol_error,expected", [(True, False, True), (False, False, False), (True, True, False)]
)
@pytest.mark.parametrize("raises", [False, True])
async def test_routed_terminal_provenance_requires_closed_transport(closed, protocol_error, expected, raises):
    error = aiohttp.WebSocketError(1002, "protocol invalid") if protocol_error else ConnectionResetError("socket ended")
    socket = SimpleNamespace(
        closed=closed,
        close_code=1006 if closed else None,
        receive=AsyncMock(
            side_effect=error if raises else None,
            return_value=aiohttp.WSMessage(aiohttp.WSMsgType.ERROR, error, None),
        ),
        exception=lambda: error,
    )
    message = await CodexUpstreamWebSocket(socket).receive()
    assert message.kind == "error"
    assert message.transport_ended is expected


@pytest.mark.asyncio
@pytest.mark.parametrize("phase,expected", [("transport", True), ("protocol", False)])
async def test_native_terminal_phase_supplies_provenance(phase, expected):
    socket = SimpleNamespace(receive=AsyncMock(side_effect=NativeEgressTransportError("failed", failure_phase=phase)))
    message = await NativeUpstreamWebSocket(socket).receive()
    assert message.transport_ended is expected


@pytest.mark.asyncio
async def test_native_protocol_fault_has_no_ending_provenance():
    socket = SimpleNamespace(receive=AsyncMock(side_effect=NativeEgressProtocolError("bad IPC")))
    message = await NativeUpstreamWebSocket(socket).receive()
    assert not message.transport_ended
