from __future__ import annotations

import asyncio
import json
from dataclasses import dataclass, field, replace

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from sqlalchemy import select

from app.core.clients import proxy as core_proxy
from app.core.clients import proxy_websocket
from app.core.types import JsonValue
from app.core.utils.sse import parse_sse_data_json
from app.db.models import ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from app.modules.proxy._service.http_bridge import helpers as bridge_helpers
from app.modules.proxy._service.http_bridge import retry_circuit
from app.modules.proxy._service.http_bridge import streaming as bridge_streaming
from tests.integration.model_source_helpers import _enable_api_key_auth
from tests.integration.test_http_responses_bridge import (
    _cleanup_http_bridge_sessions as cleanup_http_bridge_sessions,  # noqa: F401
)
from tests.integration.test_http_responses_bridge import (
    _import_account,
    _install_proxy_settings,
    _make_app_settings,
    _make_dashboard_settings,
)
from tests.integration.test_proxy_transient_retry import _success_sse_event

pytestmark = pytest.mark.integration


@dataclass
class _BridgeOrigin:
    url: str = ""
    owner_id: str = ""
    mode: str = "healthy"
    delay: float = 0.0
    frames: list[dict] = field(default_factory=list)
    connections: int = 0
    http_frames: list[dict] = field(default_factory=list)
    http_headers: list[dict[str, str]] = field(default_factory=list)


@pytest.fixture
async def bridge_origin(async_client, app_instance, monkeypatch):
    del app_instance
    owner = await _import_account(async_client, "bridge-contract-owner", "bridge-contract@example.invalid")
    await _enable_api_key_auth(async_client)
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "bridge-continuation-contract",
            "assignedAccountIds": [owner],
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 10000000}],
        },
    )
    assert created.status_code == 200
    monkeypatch.setitem(async_client.headers, "Authorization", f"Bearer {created.json()['key']}")
    settings = _make_app_settings(enabled=True).model_copy(update={"sse_keepalive_interval_seconds": 0.01})
    dashboard = _make_dashboard_settings()
    dashboard.api_key_auth_enabled = True
    _install_proxy_settings(monkeypatch, app_settings=settings, dashboard_settings=dashboard)
    monkeypatch.setattr(proxy_api, "get_settings", lambda: settings)
    monkeypatch.setattr(proxy_service, "_HTTP_BRIDGE_STARTUP_KEEPALIVE_GRACE_SECONDS", 0.01)
    state = _BridgeOrigin(owner_id=owner)

    async def upstream(request):
        websocket = web.WebSocketResponse()
        await websocket.prepare(request)
        state.connections += 1
        async for message in websocket:
            if message.type != web.WSMsgType.TEXT:
                continue
            frame = json.loads(message.data)
            state.frames.append(frame)
            if state.mode == "silent":
                continue
            if state.mode == "deny" and frame.get("previous_response_id"):
                if state.delay:
                    await websocket.send_json(
                        {"type": "response.created", "response": {"id": "resp_denied", "status": "in_progress"}}
                    )
                await asyncio.sleep(state.delay)
                await websocket.send_json(
                    {
                        "type": "error",
                        "response_id": "resp_denied" if state.delay else None,
                        "status": 400,
                        "error": {
                            "type": "invalid_request_error",
                            "code": "previous_response_not_found",
                            "param": "previous_response_id",
                            "message": "The proxy continuation anchor is unavailable.",
                        },
                    }
                )
                continue
            response_id = f"resp_contract_{len(state.frames)}"
            await websocket.send_json(
                {"type": "response.created", "response": {"id": response_id, "status": "in_progress"}}
            )
            terminal = parse_sse_data_json(_success_sse_event(response_id))
            assert terminal is not None
            response = terminal["response"]
            assert isinstance(response, dict)
            response.update(
                {
                    "object": "response",
                    "status": "completed",
                    "usage": {
                        "input_tokens": 1,
                        "output_tokens": 1,
                        "total_tokens": 2,
                        "input_tokens_details": {"cached_tokens": 0},
                        "output_tokens_details": {"reasoning_tokens": 0},
                    },
                    "output": [
                        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "OK"}]}
                    ],
                }
            )
            await websocket.send_json(terminal)
        return websocket

    origin = web.Application()
    origin.router.add_get("/codex/responses", upstream)

    async def http_upstream(request):
        state.http_frames.append(await request.json())
        state.http_headers.append(dict(request.headers))
        return web.Response(text=_success_sse_event("resp_lite_image"), content_type="text/event-stream")

    origin.router.add_post("/codex/responses", http_upstream)
    connect = proxy_websocket.connect_responses_websocket
    monkeypatch.setattr(proxy_websocket, "discover_native_egress_client", lambda: None)
    async with TestServer(origin, shutdown_timeout=0.2) as server:
        state.url = str(server.make_url(""))

        async def actual_connect(headers, token, account_id, **kwargs):
            del kwargs
            return await connect(
                headers, token, account_id, base_url=str(server.make_url("")), allow_direct_egress=True
            )

        monkeypatch.setattr(proxy_service, "connect_responses_websocket", actual_connect)
        try:
            yield state
        finally:
            service = get_proxy_service_for_app(async_client._transport.app)
            for session in list(service._http_bridge_sessions.values()):
                await service._close_http_bridge_session(session)


def _events(response) -> list[dict]:
    return [event for block in response.text.split("\n\n") if (event := parse_sse_data_json(block)) is not None]


def _user(text: str) -> dict:
    return {"role": "user", "content": [{"type": "input_text", "text": text}]}


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/backend-api/codex/responses", "/backend-api/codex/responses/"])
@pytest.mark.parametrize("after_keepalive", [False, True])
async def test_denied_proxy_anchor_delivers_one_terminal(
    async_client, app_instance, monkeypatch, bridge_origin, path, after_keepalive
):
    headers = {
        "session_id": "bridge-contract-session",
        "originator": "codex_cli_rs",
        "User-Agent": "codex_cli_rs/0.116.0",
    }
    body = {"model": "gpt-5.1", "input": [_user("first")], "stream": True, "max_output_tokens": 64}
    first = await async_client.post(path, json=body, headers=headers)
    assert first.status_code == 200, first.text
    assert _events(first)[-1]["type"] == "response.completed"
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    async with SessionLocal() as database:
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert [(row.status, row.input_tokens, row.output_tokens) for row in reservations] == [("finalized", 1, 1)]
    bridge_origin.mode = "deny"
    bridge_origin.delay = 0.08 if after_keepalive else 0.0
    monkeypatch.setattr(proxy_api, "_HTTP_BRIDGE_STARTUP_ERROR_PROBE_SECONDS", 0.0 if after_keepalive else 0.5)
    body["input"] = [
        *body["input"],
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "OK"}]},
        _user("next"),
        {"type": "item_reference", "id": "msg_owned"},
    ]
    second = await asyncio.wait_for(async_client.post(path, json=body, headers=headers), timeout=10)
    assert any(frame.get("previous_response_id") for frame in bridge_origin.frames), bridge_origin.frames
    events = _events(second)
    failed = [event for event in events if event["type"] == "response.failed"]
    if after_keepalive:
        assert second.status_code == 200, second.text
        assert len(failed) == 1, second.text
        assert any(event["type"] == "response.in_progress" for event in events), second.text
    else:
        assert second.status_code == 502, second.text
        assert second.json()["error"]["code"] == "stream_incomplete"
    assert not any(event["type"] == "response.completed" for event in events)
    assert "_codex_lb_synthetic_transport_failure" not in second.text
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert all(
        not session.pending_requests and session.queued_request_count == 0
        for session in service._http_bridge_sessions.values()
    )
    async with SessionLocal() as database:
        logs = list(await database.scalars(select(RequestLog).order_by(RequestLog.id)))
        assert len(logs) == 2
        assert logs[-1].status == "error"
        assert logs[-1].upstream_error_code == "previous_response_not_found"
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert len(reservations) >= 2
        assert all(row.status in {"released", "finalized"} for row in reservations)
    assert await service._load_balancer.account_pressure_snapshot(bridge_origin.owner_id) == (0, 0, 0.0)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("parallel", [True, False, None, "omitted"])
async def test_image_tools_lite_bypass_reaches_real_http_with_serial_calls(
    async_client, monkeypatch, bridge_origin, path, parallel
):
    dashboard = _make_dashboard_settings()
    dashboard.api_key_auth_enabled = True
    dashboard.upstream_stream_transport = "http"
    _install_proxy_settings(monkeypatch, app_settings=_make_app_settings(enabled=True), dashboard_settings=dashboard)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    monkeypatch.setattr(core_proxy, "resolve_http_proxy_from_env", lambda _url: None)

    def actual_stream(payload, headers, token, account_id, **kwargs):
        return core_proxy.stream_responses(
            payload,
            headers,
            token,
            account_id,
            base_url=bridge_origin.url,
            upstream_stream_transport_override="http",
            raise_for_status=True,
            failure_trace=kwargs.get("failure_trace"),
        )

    monkeypatch.setattr(proxy_service, "core_stream_responses", actual_stream)
    image = (
        "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJ"
        "AAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="
    )
    body = {
        "model": "gpt-5.1",
        "input": [
            {"type": "additional_tools", "role": "developer", "tools": []},
            {
                "role": "user",
                "content": [{"type": "input_text", "text": "inspect"}, {"type": "input_image", "image_url": image}],
            },
        ],
        "tools": [{"type": "function", "name": "echo", "parameters": {"type": "object", "properties": {}}}],
        "reasoning": {"effort": "high"},
        "stream": True,
    }
    if parallel != "omitted":
        body["parallel_tool_calls"] = parallel
    response = await async_client.post(path, json=body)
    assert response.status_code == 200, response.text
    assert _events(response)[-1]["type"] == "response.completed", response.text
    assert not bridge_origin.frames
    assert len(bridge_origin.http_frames) == 1
    sent = bridge_origin.http_frames[0]
    assert sent["parallel_tool_calls"] is False
    assert sent["reasoning"] == {"effort": "high", "context": "all_turns"}
    assert sent["input"] == body["input"]
    assert sent["tools"] == body["tools"]
    sent_headers = {name.lower(): value for name, value in bridge_origin.http_headers[0].items()}
    assert sent_headers[core_proxy.CODEX_RESPONSES_LITE_HEADER] == "true"


async def _seed_turn_state(service, *, owner_id: str, api_key_id: str, turn_state: str) -> list[JsonValue]:
    prior: list[JsonValue] = [_user("first")]
    claimed = await service._durable_bridge.claim_live_session(
        session_key_kind="session_header",
        session_key_value="budget-contract-session",
        api_key_id=api_key_id,
        instance_id="contract-instance",
        owner_process_epoch="contract-epoch",
        lease_ttl_seconds=60,
        account_id=owner_id,
        model="gpt-5.1",
        service_tier=None,
        latest_turn_state=turn_state,
        latest_response_id="resp_budget_prior",
        allow_takeover=True,
    )
    await service._durable_bridge.renew_live_session(
        session_id=claimed.session_id,
        api_key_id=api_key_id,
        instance_id="contract-instance",
        owner_epoch=claimed.owner_epoch,
        lease_ttl_seconds=60,
        latest_turn_state=turn_state,
        latest_response_id="resp_budget_prior",
        latest_input_item_count=1,
        latest_input_full_fingerprint=proxy_service._fingerprint_input_items(prior),
    )
    await service._durable_bridge.register_turn_state(
        session_id=claimed.session_id,
        api_key_id=api_key_id,
        instance_id="contract-instance",
        owner_epoch=claimed.owner_epoch,
        lease_ttl_seconds=60,
        turn_state=turn_state,
    )
    return prior


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/backend-api/codex/responses", "/backend-api/codex/responses/"])
@pytest.mark.parametrize(
    "history",
    ["full", "other-key", "wrong-prefix", "missing-output", "explicit-anchor", "owned-item", "owner-conflict"],
)
async def test_payload_fallback_quota_uses_scoped_durable_proof(async_client, app_instance, monkeypatch, path, history):
    await _enable_api_key_auth(async_client)
    owner = await _import_account(async_client, "budget-a", "budget-owner@example.invalid")
    alternate = await _import_account(async_client, "budget-b", "budget-alternate@example.invalid")
    keys = []
    for name in ("proof-owner", "proof-other"):
        created = await async_client.post(
            "/api/api-keys/",
            json={
                "name": name,
                "assignedAccountIds": [owner, alternate],
                "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 10000}],
            },
        )
        assert created.status_code == 200
        keys.append(created.json())
    dashboard = _make_dashboard_settings()
    dashboard.api_key_auth_enabled = True
    dashboard.upstream_stream_transport = "http"
    _install_proxy_settings(monkeypatch, app_settings=_make_app_settings(enabled=True), dashboard_settings=dashboard)
    monkeypatch.setattr(bridge_streaming, "_ws_transport_payload_budget_bytes", lambda: 1)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    monkeypatch.setattr(core_proxy, "resolve_http_proxy_from_env", lambda _url: None)
    service = get_proxy_service_for_app(app_instance)
    turn_state = "http_turn_scoped_budget"
    prior = await _seed_turn_state(service, owner_id=owner, api_key_id=keys[0]["id"], turn_state=turn_state)
    items = [*prior, {"role": "assistant", "content": [{"type": "output_text", "text": "OK"}]}, _user("next")]
    if history == "wrong-prefix":
        items[0] = _user("different")
    elif history == "missing-output":
        items.pop(1)
    elif history == "owned-item":
        items.append({"type": "item_reference", "id": "msg_owned"})
    elif history == "owner-conflict":
        lookup = service._durable_bridge.lookup_turn_state_target

        async def conflicting_lookup(**kwargs):
            result = await lookup(**kwargs)
            return replace(result, account_id=alternate) if result is not None else None

        async def conflicting_owner(**kwargs):
            del kwargs
            return owner

        monkeypatch.setattr(service._durable_bridge, "lookup_turn_state_target", conflicting_lookup)
        monkeypatch.setattr(service, "_resolve_compact_turn_state_owner", conflicting_owner)
    body = {"model": "gpt-5.1", "input": items, "stream": True}
    if history == "explicit-anchor":
        body["previous_response_id"] = "resp_budget_prior"
    calls: list[tuple[str | None, dict, dict]] = []

    async def upstream(request):
        account = request.headers.get("chatgpt-account-id")
        calls.append((account, await request.json(), dict(request.headers)))
        if account == "budget-a":
            return web.json_response(
                {
                    "error": {
                        "code": "usage_limit_reached",
                        "type": "insufficient_quota",
                        "message": "Usage limit reached",
                    }
                },
                status=429,
            )
        return web.Response(text=_success_sse_event("resp_budget_recovered"), content_type="text/event-stream")

    origin = web.Application()
    origin.router.add_post("/codex/responses", upstream)
    async with TestServer(origin) as server:

        def actual_stream(payload, headers, token, account_id, **kwargs):
            return core_proxy.stream_responses(
                payload,
                headers,
                token,
                account_id,
                base_url=str(server.make_url("")),
                upstream_stream_transport_override="http",
                raise_for_status=True,
                failure_trace=kwargs.get("failure_trace"),
            )

        monkeypatch.setattr(proxy_service, "core_stream_responses", actual_stream)
        key = keys[history == "other-key"]
        response = await async_client.post(
            path, json=body, headers={"Authorization": f"Bearer {key['key']}", "x-codex-turn-state": turn_state}
        )
    if history == "full":
        assert _events(response)[-1]["type"] == "response.completed", response.text
        assert [account for account, _, _ in calls] == ["budget-a", "budget-b"]
        assert all("x-codex-turn-state" not in {name.lower() for name in headers} for _, _, headers in calls)
        assert all(payload["input"] == items for _, payload, _ in calls)
    else:
        assert "response.completed" not in response.text, response.text
        assert not any(account == "budget-b" for account, _, _ in calls), calls
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert await service._load_balancer.account_pressure_snapshot(owner) == (0, 0, 0.0)
    assert await service._load_balancer.account_pressure_snapshot(alternate) == (0, 0, 0.0)
    async with SessionLocal() as database:
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert reservations
        assert all(row.status in {"released", "finalized"} for row in reservations)


@pytest.mark.asyncio
async def test_repeated_eventless_lineage_recovers_without_poisoned_anchor(
    async_client, app_instance, monkeypatch, bridge_origin
):
    settings = _make_app_settings(enabled=True).model_copy(
        update={
            "sse_keepalive_interval_seconds": 0.01,
            "stream_idle_timeout_seconds": 0.1,
            # This case tests downstream eventless retirement, independently
            # of the response-created retry and total request deadline.
            "proxy_request_budget_seconds": 10.0,
        }
    )
    monkeypatch.setattr(proxy_service, "get_settings", lambda: settings)
    monkeypatch.setattr(proxy_api, "get_settings", lambda: settings)
    monkeypatch.setattr(bridge_helpers, "HTTP_BRIDGE_STUCK_GATE_RETIRE_AFTER_SECONDS", 2.0)
    monkeypatch.setattr(bridge_helpers, "_HTTP_BRIDGE_EVENTLESS_RESPONSE_CREATED_MAX_SECONDS", 1.0)
    monkeypatch.setattr(retry_circuit, "_HTTP_BRIDGE_RETRY_CIRCUIT_BASE_BACKOFF_SECONDS", 0.01)
    headers = {"session_id": "bridge-silent-lineage"}
    body = {"model": "gpt-5.1", "input": [_user("first")], "stream": True, "max_output_tokens": 64}
    first = await async_client.post("/backend-api/codex/responses", json=body, headers=headers)
    assert _events(first)[-1]["type"] == "response.completed", first.text
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    body["input"] = [
        *body["input"],
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "OK"}]},
        _user("next"),
    ]
    bridge_origin.mode = "silent"
    for turn in range(2):
        body["input"][-1] = _user(f"next logical turn {turn}")
        before_attempt = len(bridge_origin.frames)
        failed = await asyncio.wait_for(
            async_client.post("/backend-api/codex/responses", json=body, headers=headers), timeout=5
        )
        assert "response.completed" not in failed.text
        assert "bridge_eventless_timeout" in failed.text, failed.text
        assert 1 <= len(bridge_origin.frames) - before_attempt <= 2, bridge_origin.frames
        assert await service.drain_persistence_tasks(timeout_seconds=5)
    attempted = len(bridge_origin.frames)
    assert 3 <= attempted <= 5, bridge_origin.frames
    bridge_origin.mode = "deny"
    recovered = await asyncio.wait_for(
        async_client.post("/backend-api/codex/responses", json=body, headers=headers), timeout=5
    )
    assert _events(recovered)[-1]["type"] == "response.completed", recovered.text
    assert all(not frame.get("previous_response_id") for frame in bridge_origin.frames[attempted:]), (
        bridge_origin.frames
    )
    assert bridge_origin.frames[-1]["input"] == body["input"]
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert all(
        not session.pending_requests and session.queued_request_count == 0
        for session in service._http_bridge_sessions.values()
    )
    async with SessionLocal() as database:
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert len(reservations) >= 4
        assert all(row.status in {"released", "finalized"} for row in reservations)
