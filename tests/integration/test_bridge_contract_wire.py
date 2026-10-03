from __future__ import annotations

import json
from copy import deepcopy
from unittest.mock import AsyncMock

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

from app.core.clients import proxy as proxy_client
from app.core.clients.proxy_websocket import CodexUpstreamWebSocket
from app.core.openai.requests import ResponsesRequest
from app.core.types import JsonValue
from app.core.utils.sse import format_sse_event, parse_sse_data_json
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import service as proxy_service
from tests.integration.test_http_responses_bridge import (
    _cleanup_http_bridge_sessions,  # noqa: F401
)
from tests.integration.test_http_responses_bridge import (
    promotion_transport as promotion_transport,
)

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("lite", [False, True])
@pytest.mark.parametrize("parallel", [None, True, False, "omitted"])
@pytest.mark.parametrize("transport", ["http", "auto"])
async def test_lite_direct_http_and_handshake_fallback_preserve_wire_contract(
    monkeypatch, lite: bool, parallel: bool | str | None, transport: str
) -> None:
    received = []

    async def upstream(request: web.Request) -> web.Response:
        if request.method == "GET":
            received.append(("GET", None, dict(request.headers)))
            return web.Response(status=426)
        received.append(("POST", await request.json(), dict(request.headers)))
        return web.Response(
            text=format_sse_event({"type": "response.completed", "response": {"id": "resp_wire"}}),
            content_type="text/event-stream",
        )

    application = web.Application()
    application.router.add_route("*", "/codex/responses", upstream)
    monkeypatch.setattr(proxy_client, "discover_native_egress_client", lambda: None)
    input_items: list[JsonValue] = [{"role": "user", "content": "hello"}]
    body: dict[str, JsonValue] = {
        "model": "gpt-5.4",
        "instructions": "",
        "stream": True,
        "input": input_items,
        "reasoning": {"effort": "high", "summary": "auto"},
        "prompt_cache_key": "wire-series",
    }
    if lite:
        input_items.insert(0, {"type": "additional_tools", "role": "developer", "tools": []})
    if parallel != "omitted":
        body["parallel_tool_calls"] = parallel
    payload = ResponsesRequest.model_validate(body)
    before = deepcopy(payload.to_payload())
    async with TestServer(application) as server, aiohttp.ClientSession() as session:
        events = [
            event
            async for event in proxy_client.stream_responses(
                payload,
                headers={"user-agent": "codex_cli_rs/0.159.3", proxy_client.CODEX_RESPONSES_LITE_HEADER: "true"},
                access_token="synthetic",
                account_id="wire-account",
                base_url=str(server.make_url("/")),
                session=session,
                upstream_stream_transport_override=transport,
            )
        ]
    assert len(events) == 1
    event = parse_sse_data_json(events[0])
    assert event is not None and event["type"] == "response.completed"
    assert [method for method, _, _ in received] == (["GET", "POST"] if transport == "auto" else ["POST"])
    _, sent, headers = received[-1]
    assert sent["input"] == before["input"]
    assert sent["prompt_cache_key"] == "wire-series"
    assert payload.to_payload() == before
    normalized_headers = {name.lower(): value for name, value in headers.items()}
    if lite:
        assert sent["parallel_tool_calls"] is False
        assert sent["reasoning"] == {"effort": "high", "summary": "auto", "context": "all_turns"}
        assert normalized_headers[proxy_client.CODEX_RESPONSES_LITE_HEADER.lower()] == "true"
    else:
        assert "parallel_tool_calls" not in sent
        assert sent["reasoning"] == before["reasoning"]
        assert proxy_client.CODEX_RESPONSES_LITE_HEADER.lower() not in normalized_headers


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["pretty", "crlf", "too_big"])
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_actual_aiohttp_socket_delivers_json_and_size_evidence(
    async_client, app_instance, promotion_transport, monkeypatch, mode: str, path: str
) -> None:
    sent = []

    async def upstream(request: web.Request) -> web.WebSocketResponse:
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        async for message in socket:
            sent.append(json.loads(message.data))
            if mode == "too_big" and len(sent) == 1:
                await socket.send_str("x" * 4096)
                continue
            frames = [
                {"type": "response.created", "response": {"id": "resp_wire", "status": "in_progress"}},
                {"type": "response.output_text.delta", "response_id": "resp_wire", "delta": "Привет\nOK"},
                {"type": "response.completed", "response": {"id": "resp_wire", "status": "completed"}},
            ]
            for frame in frames:
                text = json.dumps(frame, indent=2, ensure_ascii=False)
                if mode == "crlf":
                    text = "\r\n " + text.replace("\n", "\r\n") + "\r\n"
                await socket.send_str(text)
        return socket

    application = web.Application()
    application.router.add_get("/responses", upstream)
    service = get_proxy_service_for_app(app_instance)
    health = AsyncMock()
    monkeypatch.setattr(service, "_handle_stream_error", health)
    body = {
        "model": "gpt-5.4",
        "instructions": "",
        "input": "hello",
        "stream": True,
        "prompt_cache_key": "wire-bridge-series",
    }
    async with TestServer(application) as server, aiohttp.ClientSession() as session:

        async def connect(*args, **kwargs):
            socket = await session.ws_connect(server.make_url("/responses"), max_msg_size=1024)
            return CodexUpstreamWebSocket(socket)

        connection = AsyncMock(side_effect=connect)
        monkeypatch.setattr(proxy_service, "connect_responses_websocket", connection)
        response = await async_client.post(path, json=body)
        if mode == "too_big":
            if response.status_code == 400:
                error = response.json()["error"]
            else:
                assert response.status_code == 200
                event = next(
                    parse_sse_data_json(block) for block in response.text.split("\n\n") if "payload_too_large" in block
                )
                assert event is not None
                envelope = event.get("response", event)
                assert isinstance(envelope, dict)
                error = envelope["error"]
            assert isinstance(error, dict)
            assert error["code"] == "payload_too_large" and error["param"] == "input"
            assert len(sent) == 1 and connection.await_count == 1
            response = await async_client.post(path, json=body)
            assert connection.await_count == 2
        assert response.status_code == 200
        events = [
            event
            for block in response.text.split("\n\n")
            if (event := parse_sse_data_json(block)) is not None and event["type"] != "codex.keepalive"
        ]
        assert [event["type"] for event in events] == [
            "response.created",
            "response.output_text.delta",
            "response.completed",
        ]
        assert events[1]["delta"] == "Привет\nOK"
        health.assert_not_awaited()
        for bridge in list(service._http_bridge_sessions.values()):
            await service._close_http_bridge_session(bridge)
        await service.drain_persistence_tasks(timeout_seconds=5)
