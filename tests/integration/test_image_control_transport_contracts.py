from __future__ import annotations

import asyncio
import base64
import json
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any

import pytest
from aiohttp import ClientSession, web
from aiohttp.test_utils import TestServer
from sqlalchemy import select

from app.core.clients import proxy as core_proxy
from app.core.clients import proxy_websocket
from app.core.clients.codex import CodexClient
from app.core.openai import host_models
from app.core.upstream_proxy import ResolvedProxyEndpoint, ResolvedUpstreamRoute
from app.core.utils.sse import parse_sse_data_json
from app.db.models import Account, ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from tests.integration import test_native_sse_egress as native_sse
from tests.integration.model_source_helpers import _enable_api_key_auth
from tests.integration.test_http_responses_bridge import (
    _import_account,
    _install_proxy_settings,
    _make_app_settings,
    _make_dashboard_settings,
)

pytestmark = pytest.mark.integration
native_worker = native_sse.native_worker

_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
)
_IMAGE_URL = "data:image/png;base64," + base64.b64encode(_PNG).decode()


@dataclass
class _Origin:
    owner: str
    dashboard: Any
    mode: str = "healthy"
    connections: int = 0
    frames: list[dict[str, Any]] = field(default_factory=list)
    http_frames: list[dict[str, Any]] = field(default_factory=list)
    control: list[tuple[list[tuple[str, str]], bytes, str]] = field(default_factory=list)


def _completed(response_id: str, *, image: bool = False) -> dict[str, Any]:
    output = (
        [{"id": "ig_local", "type": "image_generation_call", "status": "completed", "result": "LOCAL_IMAGE"}]
        if image
        else [
            {
                "id": f"msg_{response_id}",
                "type": "message",
                "role": "assistant",
                "status": "completed",
                "content": [{"type": "output_text", "text": "OK"}],
            }
        ]
    )
    return {
        "type": "response.completed",
        "response": {
            "id": response_id,
            "object": "response",
            "status": "completed",
            "output": output,
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "total_tokens": 2,
                "input_tokens_details": {"cached_tokens": 0},
                "output_tokens_details": {"reasoning_tokens": 0},
            },
        },
    }


@pytest.fixture
async def image_control_origin(async_client, app_instance, monkeypatch):
    owner = await _import_account(async_client, "image-control-owner", "image-control@example.invalid")
    await _enable_api_key_auth(async_client)
    key = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "image-control-contract",
            "assignedAccountIds": [owner],
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 10000000}],
        },
    )
    assert key.status_code == 200, key.text
    monkeypatch.setitem(async_client.headers, "Authorization", f"Bearer {key.json()['key']}")
    dashboard = _make_dashboard_settings()
    dashboard.api_key_auth_enabled = True
    state = _Origin(owner=owner, dashboard=dashboard)

    async def websocket_origin(request):
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        state.connections += 1
        async for message in socket:
            if message.type != web.WSMsgType.TEXT:
                continue
            frame = json.loads(message.data)
            state.frames.append(frame)
            has_image = "input_image" in message.data
            if has_image and state.mode == "silent":
                continue
            if has_image and state.mode == "invalid_image":
                await socket.send_json(
                    {
                        "type": "error",
                        "status": 400,
                        "error": {
                            "type": "invalid_request_error",
                            "code": "invalid_image",
                            "param": "input",
                            "message": "Invalid image: local test rejection.",
                        },
                    }
                )
                continue
            response_id = f"resp_image_control_{len(state.frames)}"
            await socket.send_json(
                {"type": "response.created", "response": {"id": response_id, "status": "in_progress"}}
            )
            await socket.send_json(_completed(response_id))
        return socket

    async def http_origin(request):
        frame = await request.json()
        state.http_frames.append(frame)
        # A local rejection control models the incompatibility reported in UP-PR-2537.
        if frame["model"] == "gpt-5.6-luna":
            return web.json_response(
                {"error": {"type": "invalid_request_error", "code": "unsupported_tool", "message": "Luna refused"}},
                status=400,
            )
        return web.Response(
            text=f"data: {json.dumps(_completed('resp_image_host', image=True))}\n\n",
            content_type="text/event-stream",
        )

    async def control_origin(request):
        state.control.append(
            ([(k.decode(), v.decode()) for k, v in request.raw_headers], await request.read(), request.query_string)
        )
        return web.json_response({"ok": True})

    origin = web.Application()
    origin.router.add_get("/codex/responses", websocket_origin)
    origin.router.add_post("/codex/responses", http_origin)
    origin.router.add_route("*", "/codex/{path:.*}", control_origin)
    connect = proxy_websocket.connect_responses_websocket
    monkeypatch.setattr(proxy_websocket, "discover_native_egress_client", lambda: None)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(origin, shutdown_timeout=0.2) as server, ClientSession() as http:
        base_url = str(server.make_url(""))
        settings = _make_app_settings(enabled=True).model_copy(
            update={
                "upstream_base_url": base_url,
                "proxy_request_budget_seconds": 2.0,
                "stream_idle_timeout_seconds": 0.25,
            }
        )
        _install_proxy_settings(monkeypatch, app_settings=settings, dashboard_settings=dashboard)
        monkeypatch.setattr(core_proxy, "get_settings", lambda: settings)
        monkeypatch.setattr(proxy_api, "get_settings", lambda: settings)

        async def actual_connect(headers, token, account_id, **kwargs):
            del kwargs
            return await connect(headers, token, account_id, base_url=base_url, allow_direct_egress=True)

        async def actual_control(path, **kwargs):
            kwargs.update(base_url=base_url, session=http)
            return await core_proxy.codex_control_request(path, **kwargs)

        monkeypatch.setattr(proxy_service, "connect_responses_websocket", actual_connect)
        monkeypatch.setattr(proxy_service, "core_codex_control_request", actual_control)
        try:
            yield state
        finally:
            service = get_proxy_service_for_app(app_instance)
            for bridge in list(service._http_bridge_sessions.values()):
                await service._close_http_bridge_session(bridge)
            assert await service.drain_persistence_tasks(timeout_seconds=5)


def _turn(image: bool = False) -> dict[str, Any]:
    content: list[dict[str, str]] = [{"type": "input_text", "text": "describe" if image else "hello"}]
    if image:
        content.append({"type": "input_image", "image_url": _IMAGE_URL})
    return {"role": "user", "content": content}


def _events(response) -> list[dict]:
    return [event for block in response.text.split("\n\n") if (event := parse_sse_data_json(block)) is not None]


async def _assert_settled(app_instance, state: _Origin) -> None:
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    async with SessionLocal() as database:
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert reservations
        assert all(row.status in {"released", "finalized"} for row in reservations)
        account = await database.get(Account, state.owner)
        assert account is not None and account.status.value == "active"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses"])
async def test_inline_image_history_reuses_real_socket(async_client, app_instance, image_control_origin, path):
    state = image_control_origin
    body = {"model": "gpt-5.1", "input": [_turn()], "stream": True, "prompt_cache_key": "image-wire-thread"}
    for turn in range(3):
        if turn:
            body["input"].append(_turn(image=turn == 1))
        response = await async_client.post(path, json=body, follow_redirects=True)
        assert response.status_code == 200, response.text
        assert _events(response)[-1]["type"] == "response.completed"
    assert state.connections == 1
    assert len(state.frames) == 3
    assert _IMAGE_URL in json.dumps(state.frames[1]) and _IMAGE_URL in json.dumps(state.frames[2])
    assert all(frame["prompt_cache_key"] == "image-wire-thread" for frame in state.frames)
    assert not state.http_frames
    await _assert_settled(app_instance, state)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["invalid_image", "silent"])
async def test_image_terminal_settles_without_duplicate_dispatch(
    async_client, app_instance, image_control_origin, mode
):
    state = image_control_origin
    state.mode = mode
    body = {"model": "gpt-5.1", "input": [_turn(image=True)], "stream": True, "prompt_cache_key": "image-error-thread"}
    response = await asyncio.wait_for(async_client.post("/v1/responses", json=body), timeout=8)
    if mode == "invalid_image":
        assert response.status_code == 400, response.text
        assert response.json()["error"]["code"] == "invalid_image"
    else:
        assert response.status_code >= 400 or _events(response)[-1]["type"] == "response.failed"
    assert len(state.frames) == 1, state.frames
    await _assert_settled(app_instance, state)
    state.mode = "healthy"
    body.update(input=[_turn()], prompt_cache_key="image-after-error-thread")
    recovery = await async_client.post("/v1/responses", json=body)
    assert recovery.status_code == 200, recovery.text
    assert _events(recovery)[-1]["type"] == "response.completed"
    assert len(state.frames) == 2
    await _assert_settled(app_instance, state)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/alpha/search", "/backend-api/codex/alpha/search/"])
@pytest.mark.parametrize("native", [False, True])
@pytest.mark.parametrize(
    "media_type,body",
    [("application/json", b'{"query":"test"}'), ("application/sdp", b"v=0\r\n"), ("application/json", b"")],
)
async def test_control_route_sends_one_or_zero_wire_media_types(
    async_client, image_control_origin, path, native, media_type, body
):
    state = image_control_origin
    headers = {
        "Content-Type": media_type,
        "User-Agent": "codex_cli_rs/0.116.0" if native else "test-sdk/1.0",
    }
    response = await async_client.post(path + "?tag=one&tag=two", content=body, headers=headers)
    assert response.status_code == 200, response.text
    sent_headers, sent_body, query = state.control[0]
    media_types = [(name, value) for name, value in sent_headers if name.lower() == "content-type"]
    assert [value for _, value in media_types] == ([media_type] if body else [])
    assert sent_body == body and query == "tag=one&tag=two"
    assert len(state.control) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [None, b"", b"v=0\r\n"])
@pytest.mark.parametrize("adapter", ["python", "native"])
async def test_routed_control_media_type_on_real_http_proxy(monkeypatch, native_worker, payload, adapter):
    from app.core.clients import codex as codex_client_module

    monkeypatch.setattr(codex_client_module, "discover_native_egress_client", lambda: None)
    captured: list[tuple[list[str], bytes]] = []

    async def proxy_origin(request):
        captured.append((request.headers.getall("Content-Type", []), await request.read()))
        return web.json_response({"ok": True})

    origin = web.Application()
    origin.router.add_route("*", "/{path:.*}", proxy_origin)
    async with TestServer(origin) as server, ClientSession() as session:
        assert server.port is not None
        route = ResolvedUpstreamRoute(
            mode="account_bound",
            pool_id="control-wire-pool",
            endpoint=ResolvedProxyEndpoint("control-wire-proxy", "http", "127.0.0.1", server.port),
        )
        client = CodexClient(
            session if adapter == "python" else native_sse._UnexpectedPythonSession(),
            native_egress_client=native_worker if adapter == "native" else None,
        )
        response = await core_proxy.codex_control_request(
            "alpha/search",
            method="POST",
            payload=payload,
            query_params=[],
            headers={"Content-Type": "application/sdp", "user-agent": "codex_cli_rs/0.116.0"},
            access_token="local-wire-token",
            account_id="local-wire-owner",
            base_url="http://origin.invalid",
            route=route,
            codex_client=client,
        )
        assert response.status_code == 200
        assert captured == [(["application/sdp"] if payload else [], payload or b"")]


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", ["generations", "edits"])
@pytest.mark.parametrize("prefix", ["/v1", "/backend-api/codex"])
@pytest.mark.parametrize("host", ["gpt-5.6-sol", "gpt-6-astra", "gpt-5.5"])
async def test_images_route_uses_compatible_host_and_public_tool_model(
    async_client, app_instance, monkeypatch, image_control_origin, operation, prefix, host
):
    state = image_control_origin
    state.dashboard.upstream_stream_transport = "http"
    registry = SimpleNamespace(
        plan_types_for_model=lambda model: {"plus"} if model in {host, "gpt-5.6-luna"} else set(),
        is_suppressed_model=lambda model: False,
    )
    monkeypatch.setattr(host_models, "get_model_registry", lambda: registry)
    public_model = "gpt-image-1"
    path = f"{prefix}/images/{operation}"
    slash = await async_client.post(path + "/", json={"model": public_model, "prompt": "a tree"})
    assert slash.status_code == 405
    assert not state.http_frames and not state.frames
    if operation == "generations":
        response = await async_client.post(
            path, json={"model": public_model, "prompt": "a tree"}, follow_redirects=True
        )
    elif prefix == "/v1":
        response = await async_client.post(
            path,
            data={"model": public_model, "prompt": "make it green"},
            files={"image": ("image.png", _PNG, "image/png")},
            follow_redirects=True,
        )
    else:
        response = await async_client.post(
            path,
            json={"model": public_model, "prompt": "make it green", "images": [{"image_url": _IMAGE_URL}]},
            follow_redirects=True,
        )
    assert response.status_code == 200, response.text
    assert response.json()["data"][0]["b64_json"] == "LOCAL_IMAGE"
    assert len(state.http_frames) == 1 and not state.frames
    frame = state.http_frames[0]
    assert frame["model"] == host
    assert frame["tool_choice"] == {"type": "image_generation"}
    image_tool = next(tool for tool in frame["tools"] if tool["type"] == "image_generation")
    assert image_tool["model"] == public_model
    if operation == "edits":
        assert _IMAGE_URL in json.dumps(frame["input"])
    await _assert_settled(app_instance, state)
    async with SessionLocal() as database:
        logs = list(await database.scalars(select(RequestLog)))
        assert logs and all(row.model == public_model for row in logs)
