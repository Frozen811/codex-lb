from __future__ import annotations

import json
import time

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.core.openai.models import OpenAIResponsePayload
from app.core.openai.requests import ResponsesRequest
from app.core.usage.models import UsagePayload
from app.db.models import Account, AccountStatus, ApiKeyUsageReservation, StickySession, StickySessionKind
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.accounts.service import AccountsService
from app.modules.proxy import api as proxy_api
from app.modules.proxy import model_account_routing as routing
from app.modules.proxy import subagent_preference
from app.modules.proxy.affinity import _sticky_key_for_responses_request
from tests.integration import test_http_responses_bridge as bridge
from tests.integration.test_accounts_api_probe import _import_test_account
from tests.integration.test_api_keys_api import _settle_account_import_invalidations

pytestmark = pytest.mark.integration
PATHS = ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
MODEL = "gpt-5.1"
BODY = {"model": MODEL, "instructions": "", "input": "Synthetic task", "stream": True}


@pytest.fixture(autouse=True)
def clean_routes():
    routing.clear_model_account_routes()
    yield
    routing.clear_model_account_routes()


@pytest_asyncio.fixture
async def placement(async_client, app_instance, monkeypatch):
    dashboard = bridge._make_dashboard_settings()
    bridge._install_proxy_settings(
        monkeypatch, app_settings=bridge._make_app_settings(enabled=True), dashboard_settings=dashboard
    )
    monkeypatch.setattr(subagent_preference, "get_settings_cache", lambda: bridge._SettingsCache(dashboard))
    ids = [
        await bridge._import_account(async_client, f"placement-{suffix}", f"placement-{suffix}@example.invalid")
        for suffix in ("a", "b")
    ]
    await _settle_account_import_invalidations()
    calls = []
    sockets = {}

    async def fresh(account, **kwargs):
        return account

    async def connect(headers, access_token, account_id, **kwargs):
        calls.append(account_id)
        socket = bridge._FakeBridgeUpstreamWebSocket(f"resp_{account_id}")
        sockets[account_id] = socket
        return socket

    async def stream(payload, headers, access_token, account_id, **kwargs):
        calls.append(account_id)
        yield (
            'data: {"type":"response.completed",'
            '"response":{"id":"resp_placement","status":"completed","output":[]}}\n\n'
        )

    async def compact(payload, headers, access_token, account_id, **kwargs):
        calls.append(account_id)
        return OpenAIResponsePayload.model_validate({"output": []})

    service = get_proxy_service_for_app(app_instance)
    monkeypatch.setattr(service, "_ensure_fresh_with_budget", fresh)
    monkeypatch.setattr(bridge.proxy_module, "connect_responses_websocket", connect)
    monkeypatch.setattr(bridge.proxy_module, "core_stream_responses", stream)
    monkeypatch.setattr(bridge.proxy_module, "core_compact_responses", compact)
    try:
        yield service, ids, calls, sockets, dashboard
    finally:
        await service.close_all_http_bridge_sessions()


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("transport", ["http", "bridge", "compact"])
async def test_strict_header_overrides_registered_route(async_client, placement, monkeypatch, path, transport):
    service, ids, calls, _sockets, dashboard = placement
    if transport != "bridge":
        dashboard.http_downstream_transport_policy = "always_http"
        bridge._install_proxy_settings(
            monkeypatch, app_settings=bridge._make_app_settings(enabled=False), dashboard_settings=dashboard
        )
    routing.register_model_account_route(MODEL, ids[0])
    if transport == "compact":
        path = path.rstrip("/") + "/compact" + ("/" if path.endswith("/") else "")
    response = await async_client.post(
        path, json=BODY, headers={routing.MODEL_ACCOUNT_ROUTING_HEADER: f"{MODEL}={ids[1]}"}
    )
    assert response.status_code == 200, response.text
    assert calls == ["placement-b"]
    assert await service._load_balancer.account_pressure_snapshot(ids[0]) == (0, 0, 0.0)


@pytest.mark.parametrize("path", PATHS)
async def test_strict_route_rejects_unavailable_target(async_client, placement, path):
    service, ids, calls, _sockets, _dashboard = placement
    async with SessionLocal() as session:
        account = await session.get(Account, ids[0])
        assert account is not None
        account.status = AccountStatus.PAUSED
        await session.commit()
    routing.register_model_account_route(MODEL, ids[0])
    response = await async_client.post(path, json=BODY)
    assert response.status_code == 503, response.text
    assert response.json()["error"]["code"] == "model_account_unavailable"
    assert calls == []
    assert await service._load_balancer.account_pressure_snapshot(ids[0]) == (0, 0, 0.0)


@pytest.mark.parametrize("path", PATHS)
async def test_warm_bridge_strict_route_preserves_required_owner(async_client, placement, path):
    _service, ids, calls, sockets, _dashboard = placement
    headers = {
        "session-id": "placement-thread",
        "thread-id": "placement-thread",
        routing.MODEL_ACCOUNT_ROUTING_HEADER: f"{MODEL}={ids[0]}",
    }
    first = await async_client.post(path, json=BODY, headers=headers)
    assert first.status_code == 200 and "response.completed" in first.text, first.text
    events = [json.loads(line[6:]) for line in first.text.splitlines() if line.startswith("data: {")]
    response_id = next(event["response"]["id"] for event in events if event["type"] == "response.completed")
    headers[routing.MODEL_ACCOUNT_ROUTING_HEADER] = f"{MODEL}={ids[1]}"
    second = await async_client.post(path, json={**BODY, "previous_response_id": response_id}, headers=headers)
    assert second.status_code == 503, second.text
    assert second.json()["error"]["code"] == "model_account_owner_conflict"
    assert calls == ["placement-a"]
    assert len(sockets["placement-a"].sent_text) == 1


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("ttl", [120, 3600])
async def test_child_bridge_retention_and_idle_cleanup(async_client, placement, path, ttl):
    service, ids, _calls, _sockets, dashboard = placement
    dashboard.openai_cache_affinity_max_age_seconds = ttl
    headers = {"session-id": "child-process", "thread-id": "child-thread", "x-parent-session-id": "parent"}
    response = await async_client.post(path, json=BODY, headers=headers)
    assert response.status_code == 200 and "response.completed" in response.text, response.text
    sessions = list(service._http_bridge_sessions.values())
    assert len(sessions) == 1
    child = sessions[0]
    assert child.idle_ttl_seconds == min(ttl, 300)
    child.last_used_at -= child.idle_ttl_seconds + 1
    async with service._http_bridge_lock:
        expired = service._prune_http_bridge_sessions_locked()
    assert expired == [child]
    await service._close_http_bridge_session(child)
    assert child.closed
    assert await service._load_balancer.account_pressure_snapshot(child.account.id) == (0, 0, 0.0)


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("scenario", ["header", "warm_conflict"])
def test_native_websocket_strict_header(app_instance, monkeypatch, path, scenario):
    dashboard = bridge._make_dashboard_settings()
    bridge._install_proxy_settings(
        monkeypatch, app_settings=bridge._make_app_settings(enabled=False), dashboard_settings=dashboard
    )
    calls = []

    async def authorize(_authorization, *, request=None):
        return None

    monkeypatch.setattr(proxy_api, "validate_proxy_api_key_authorization", authorize)

    async def fresh(self, account, **kwargs):
        return account

    async def connect(headers, access_token, account_id, **kwargs):
        calls.append(account_id)
        return bridge._FakeBridgeUpstreamWebSocket("resp_native_placement")

    monkeypatch.setattr(bridge.proxy_module.ProxyService, "_ensure_fresh_with_budget", fresh)
    monkeypatch.setattr(bridge.proxy_module, "connect_responses_websocket", connect)
    with TestClient(app_instance, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        ids = []
        for suffix in ("a", "b"):
            response = client.post(
                "/api/accounts/import",
                files={
                    "auth_json": (
                        "auth.json",
                        json.dumps(
                            bridge._make_auth_json(
                                f"native-placement-{suffix}", f"native-placement-{suffix}@example.invalid"
                            )
                        ),
                    )
                },
            )
            assert response.status_code == 200, response.text
            ids.append(response.json()["accountId"])
        assert client.portal is not None
        client.portal.call(_settle_account_import_invalidations)
        routing.register_model_account_route(MODEL, ids[0] if scenario == "header" else ids[1])
        headers = {routing.MODEL_ACCOUNT_ROUTING_HEADER: f"{MODEL}={ids[1]}"} if scenario == "header" else {}
        with client.websocket_connect(path, headers=headers) as websocket:
            websocket.send_json({**BODY, "type": "response.create"})
            for _ in range(10):
                event = websocket.receive_json()
                if event["type"] == "response.completed":
                    break
            else:
                pytest.fail("Missing native terminal")
            if scenario == "warm_conflict":
                routing.register_model_account_route(MODEL, ids[0])
                websocket.send_json(
                    {**BODY, "type": "response.create", "previous_response_id": event["response"]["id"]}
                )
                terminal = websocket.receive_json()
                error = terminal.get("error") or terminal.get("response", {}).get("error")
                assert error and error["code"] == "model_account_owner_conflict", terminal
    assert calls == ["native-placement-b"]


@pytest.mark.parametrize("path", PATHS)
async def test_child_reuse_shortens_parent_bridge_retention(async_client, placement, path):
    service, _ids, calls, _sockets, _dashboard = placement
    headers = {"session-id": "retained-process", "thread-id": "retained-thread"}
    first = await async_client.post(path, json=BODY, headers=headers)
    assert first.status_code == 200 and "response.completed" in first.text
    retained = next(iter(service._http_bridge_sessions.values()))
    assert retained.idle_ttl_seconds > 300
    headers["x-parent-session-id"] = "parent"
    second = await async_client.post(path, json=BODY, headers=headers)
    assert second.status_code == 200 and "response.completed" in second.text, second.text
    assert next(iter(service._http_bridge_sessions.values())) is retained
    assert retained.idle_ttl_seconds <= 300 and len(calls) == 1


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("transport", ["http", "bridge", "compact"])
async def test_strict_header_cannot_escape_key_scope(async_client, placement, monkeypatch, path, transport):
    _service, ids, calls, _sockets, dashboard = placement
    dashboard.api_key_auth_enabled = True
    enabled = await async_client.put("/api/settings", json={"apiKeyAuthEnabled": True})
    assert enabled.status_code == 200, enabled.text
    if transport != "bridge":
        dashboard.http_downstream_transport_policy = "always_http"
        bridge._install_proxy_settings(
            monkeypatch, app_settings=bridge._make_app_settings(enabled=False), dashboard_settings=dashboard
        )
    key = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "strict-scope",
            "assignedAccountIds": [ids[0]],
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 20000}],
        },
    )
    assert key.status_code == 200, key.text
    assigned = await async_client.patch(f"/api/api-keys/{key.json()['id']}", json={"assignedAccountIds": [ids[0]]})
    assert assigned.status_code == 200 and assigned.json()["accountAssignmentScopeEnabled"] is True, assigned.text
    headers = {
        "Authorization": f"Bearer {key.json()['key']}",
        routing.MODEL_ACCOUNT_ROUTING_HEADER: f"{MODEL}={ids[1]}",
    }
    if transport == "compact":
        path = path.rstrip("/") + "/compact" + ("/" if path.endswith("/") else "")
    response = await async_client.post(path, json=BODY, headers=headers)
    if "application/json" in response.headers["content-type"]:
        error = response.json()["error"]
    else:
        events = [json.loads(line[6:]) for line in response.text.splitlines() if line.startswith("data: {")]
        assert events[-1]["type"] == "response.failed", response.text
        error = events[-1]["response"]["error"]
    assert error["code"] == "model_account_scope_mismatch", response.text
    assert calls == []
    async with SessionLocal() as session:
        reservations = (await session.scalars(select(ApiKeyUsageReservation))).all()
        assert all(row.status != "reserved" for row in reservations)


@pytest.mark.parametrize("path", ["/backend-api/codex/responses", "/backend-api/codex/responses/"])
@pytest.mark.parametrize("scenario", ["alternate", "fallback", "established"])
async def test_product_child_account_preference(async_client, placement, monkeypatch, path, scenario):
    service, ids, calls, _sockets, dashboard = placement
    selections = []
    selector = service._select_account_with_budget_compatible

    async def observe(deadline, **kwargs):
        observed = kwargs["affinity_policy"]
        selections.append(
            (
                kwargs.get("request_stage"),
                observed.codex_session_source,
                observed.subagent_parent_response_marker_key,
                observed.selection_key,
            )
        )
        return await selector(deadline, **kwargs)

    monkeypatch.setattr(service, "_select_account_with_budget_compatible", observe)
    dashboard.subagent_account_preference = "parent_bound_only"
    headers = {
        "session-id": "child-process",
        "thread-id": "child-thread",
        "x-openai-subagent": "collab_spawn",
        "x-codex-parent-thread-id": "parent-thread",
    }
    policy = _sticky_key_for_responses_request(
        ResponsesRequest.model_validate(BODY),
        headers,
        codex_session_affinity=True,
        openai_cache_affinity=True,
        openai_cache_affinity_max_age_seconds=300,
        sticky_threads_enabled=False,
    )
    assert policy.subagent_parent_response_marker_key
    async with SessionLocal() as session:
        session.add(
            StickySession(
                key=policy.subagent_parent_response_marker_key, kind=StickySessionKind.CODEX_SESSION, account_id=ids[0]
            )
        )
        if scenario == "fallback":
            row = await session.get(Account, ids[1])
            assert row is not None
            row.status = AccountStatus.PAUSED
        elif scenario == "established":
            session.add(StickySession(key=policy.selection_key, kind=policy.kind, account_id=ids[0]))
        await session.commit()
    response = await async_client.post(path, json=BODY, headers=headers)
    assert response.status_code == 200 and "response.completed" in response.text, response.text
    assert calls == ["placement-b" if scenario == "alternate" else "placement-a"], selections
    assert selections[0][0] == "follow_up"
    assert selections[0][2] == policy.subagent_parent_response_marker_key


@pytest.mark.parametrize("outcome", ["available", "failed", "exhausted", "operator_race"])
async def test_verified_probe_preserves_negative_and_raced_holds(async_client, monkeypatch, outcome):
    account_id = await _import_test_account(
        async_client, email="probe-boundary@example.invalid", account_id="probe-boundary"
    )
    now = int(time.time())
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        account.status = AccountStatus.RATE_LIMITED
        account.blocked_at = now - 5
        account.reset_at = now + 3600
        await session.commit()
    probes = []

    async def probe(self, *, access_token, chatgpt_account_id, model):
        probes.append((chatgpt_account_id, model))
        return 429 if outcome == "failed" else 200

    async def usage(**kwargs):
        if outcome == "operator_race":
            async with SessionLocal() as session:
                account = await session.get(Account, account_id)
                assert account is not None
                account.status = AccountStatus.PAUSED
                await session.commit()
        return UsagePayload.model_validate(
            {
                "plan_type": "pro",
                "rate_limit": {
                    "primary_window": {
                        "used_percent": 100 if outcome == "exhausted" else 0,
                        "reset_at": now + 3600,
                        "window_minutes": 300,
                    },
                    "secondary_window": {"used_percent": 10, "reset_at": now + 86400, "window_minutes": 10080},
                },
            }
        )

    monkeypatch.setattr(AccountsService, "_send_probe_request", probe)
    monkeypatch.setattr("app.modules.usage.updater.fetch_usage", usage)
    response = await async_client.post(f"/api/accounts/{account_id}/probe", json={"model": MODEL})
    assert response.status_code == 200, response.text
    assert probes == [("probe-boundary", MODEL)]
    expected = "active" if outcome == "available" else "paused" if outcome == "operator_race" else "rate_limited"
    assert response.json()["accountStatusAfter"] == expected
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        assert account.status.value == expected
        if outcome == "available":
            assert account.reset_at is None and account.blocked_at is None
        else:
            assert account.reset_at == now + 3600 and account.blocked_at == now - 5
