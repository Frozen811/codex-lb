from __future__ import annotations

import asyncio
import json

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.core.clients import proxy_websocket
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import service as proxy_service
from tests.integration.test_http_responses_bridge import _import_account, _install_bridge_settings

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("boundary", ["\n", "\r\n", "\r"])
@pytest.mark.parametrize("committed", [False, True])
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
async def test_multiline_websocket_refusal_reaches_http_bridge_promptly(
    async_client, app_instance, monkeypatch, boundary, committed, path
):
    await _import_account(async_client, "multiline-owner", "multiline@example.invalid")
    _install_bridge_settings(monkeypatch, enabled=True)
    monkeypatch.setattr(proxy_websocket, "discover_native_egress_client", lambda: None)
    message = "Input must mention 'json'. Привет"
    observed = []

    async def upstream(request):
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        observed.append(await socket.receive_json())
        if committed:
            await socket.send_str(
                json.dumps(
                    {
                        "type": "response.created",
                        "response": {"id": "resp_multiline", "status": "in_progress", "model": "gpt-5.2", "output": []},
                    },
                    indent=2,
                ).replace("\n", boundary)
            )
        payload = {
            "type": "error",
            "status": 400,
            "error": {"type": "invalid_request_error", "code": None, "message": message, "param": "input"},
        }
        await socket.send_str(json.dumps(payload, ensure_ascii=False, indent=2).replace("\n", boundary))
        async for _ in socket:
            pass
        return socket

    application = web.Application()
    application.router.add_get("/codex/responses", upstream)
    service = get_proxy_service_for_app(app_instance)
    async with TestServer(application) as server:

        async def connect_local(headers, access_token, account_id, **kwargs):
            return await proxy_websocket.connect_responses_websocket(
                headers, access_token, account_id, base_url=str(server.make_url("/")), allow_direct_egress=True
            )

        monkeypatch.setattr(proxy_service, "connect_responses_websocket", connect_local)
        try:
            async with asyncio.timeout(5):
                response = await async_client.post(
                    path, json={"model": "gpt-5.2", "input": "test", "stream": True}, follow_redirects=True
                )
            assert len(observed) == 1 and observed[0]["type"] == "response.create"
            if committed or path.startswith("/backend-api/"):
                assert response.status_code == 200, response.text
                events = [
                    json.loads(line[6:])
                    for line in response.text.splitlines()
                    if line.startswith("data: ") and line[6:] != "[DONE]"
                ]
                terminals = [event for event in events if event.get("type") in {"response.failed", "error"}]
                assert len(terminals) == 1
                terminal = terminals[0]
                error = terminal["response"]["error"] if terminal["type"] == "response.failed" else terminal["error"]
                assert error["message"] == message
                assert any(event.get("type") == "response.created" for event in events) is committed
            else:
                assert response.status_code == 400, response.text
                assert response.json()["error"]["message"] == message
        finally:
            for session in list(service._http_bridge_sessions.values()):
                await service._close_http_bridge_session(session)
