from __future__ import annotations

import json

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.core.clients import proxy as core_proxy
from app.core.clients import proxy_websocket
from app.modules.proxy import service as proxy_service
from tests.integration.test_plan_json_contracts import _import_plan

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("identity", ["ccodex-internal", "ccodex-handoff-worker"])
@pytest.mark.parametrize("transport", ["http", "websocket"])
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_ccodex_identity_reaches_actual_upstream(async_client, monkeypatch, identity, transport, path):
    await _import_plan(async_client, "pro")
    observed = []
    user_agent = f"{identity}/0.159.3 (Ubuntu 24.4.0; x86_64) unknown (Codex Desktop; fixture)"

    async def upstream(request):
        observed.append(dict(request.headers))
        event = {
            "type": "response.completed",
            "response": {
                "id": "resp_gateway_wire",
                "status": "completed",
                "model": "gpt-6.1-sol",
                "output": [],
                "usage": {"input_tokens": 10, "output_tokens": 1},
            },
        }
        if transport == "websocket":
            socket = web.WebSocketResponse()
            await socket.prepare(request)
            payload = await socket.receive_json()
            assert payload["type"] == "response.create"
            await socket.send_json(event)
            await socket.close()
            return socket
        assert (await request.json())["model"] == "gpt-6.1-sol"
        return web.Response(text=f"data: {json.dumps(event)}\n\n", content_type="text/event-stream")

    application = web.Application()
    application.router.add_route("*", "/codex/responses", upstream)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    monkeypatch.setattr(proxy_websocket, "discover_native_egress_client", lambda: None)
    async with TestServer(application) as server, aiohttp.ClientSession() as session:

        async def stream_local(payload, headers, access_token, account_id, **kwargs):
            async for event in core_proxy.stream_responses(
                payload,
                headers,
                access_token,
                account_id,
                base_url=str(server.make_url("/")),
                session=session,
                upstream_stream_transport_override=transport,
            ):
                yield event

        monkeypatch.setattr(proxy_service, "core_stream_responses", stream_local)
        response = await async_client.post(
            path,
            headers={"User-Agent": user_agent, "originator": identity, "version": "0.159.3"},
            json={"model": "gpt-6.1-sol", "input": "gateway test", "stream": True},
        )
        assert response.status_code == 200, response.text
        assert "resp_gateway_wire" in response.text
    assert len(observed) == 1
    headers = {key.lower(): value for key, value in observed[0].items()}
    assert headers["user-agent"] == user_agent
    assert headers["originator"] == identity
    assert headers["version"] == "0.159.3"
