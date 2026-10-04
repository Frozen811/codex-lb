from __future__ import annotations

import asyncio
import sqlite3
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from app.core.clients.proxy import ProxyResponseError
from app.db.models import ApiKeyUsageReservation, RequestLog, StickySessionKind
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from app.modules.proxy._service.http_bridge import helpers as bridge_helpers
from app.modules.proxy._service.http_bridge import mixin as bridge_mixin
from app.modules.proxy.http_bridge_forwarding import (
    HTTP_BRIDGE_LOCAL_PRE_DISPATCH_REFUSAL_HEADER,
    HTTPBridgeForwardContext,
    build_owner_forward_headers,
)
from app.modules.proxy.sticky_repository import StickySessionsRepository
from tests.integration.test_bridge_continuation_contracts import _events, _user
from tests.integration.test_bridge_continuation_contracts import bridge_origin as _bridge_origin_fixture
from tests.integration.test_http_responses_bridge import _client_reporting_committed_stream_failures, _import_account

pytestmark = pytest.mark.integration
bridge_origin = _bridge_origin_fixture
PATHS = ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses"]


def _commit_before_refusal(service, monkeypatch):
    original_stream = service._stream_via_http_bridge

    async def committed(*args, **kwargs):
        yield (
            'data: {"type":"response.in_progress","response":{"id":"resp_local_startup","status":"in_progress"}}\n\n'
        )
        stream = original_stream(*args, **kwargs)
        try:
            async for event in stream:
                yield event
        finally:
            await stream.aclose()

    monkeypatch.setattr(service, "_stream_via_http_bridge", committed)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "after_commit"),
    [(path, False) for path in [*PATHS, "/internal/bridge/responses"]] + [("/backend-api/codex/responses", True)],
)
@pytest.mark.parametrize(
    "refusal",
    [
        "cooldown",
        "generation",
        "retiring",
        "unregistered",
        "reconnect",
        "late_closed",
        "lease_race",
        "startup_cooldown",
    ],
)
async def test_native_local_refusal_is_delivered_before_dispatch(
    async_client, app_instance, bridge_origin, monkeypatch, path, refusal, after_commit
):
    headers = {"session_id": "local-refusal-contract", "User-Agent": "codex_exec/0.153.4", "originator": "codex_cli_rs"}

    async def post(body):
        body = {"instructions": "hi", **body}
        if path in {"/backend-api/codex/responses", "/internal/bridge/responses"}:
            body.pop("stream", None)
        if path == "/internal/bridge/responses":
            payload = proxy_service.ResponsesRequest.model_validate(body)
            signed_headers = build_owner_forward_headers(
                headers=headers,
                payload=payload,
                context=HTTPBridgeForwardContext(
                    origin_instance="instance-b",
                    target_instance="instance-a",
                    codex_session_affinity=True,
                    downstream_turn_state=None,
                    original_request_unanchored=body.get("previous_response_id") is None,
                    original_affinity_kind="session_header",
                    original_affinity_key=headers["session_id"],
                ),
            )
            body = payload.model_dump_for_forwarding()
            request_headers = signed_headers
        else:
            request_headers = headers
        async with _client_reporting_committed_stream_failures(app_instance) as wire_client:
            wire_client.headers.update(async_client.headers)
            return await wire_client.post(path, headers=request_headers, json=body)

    seed = await post({"model": "gpt-5.1", "input": [_user("seed")], "stream": True})
    assert seed.status_code == 200, seed.text
    assert _events(seed)[-1]["type"] == "response.completed"
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    session = next(iter(service._http_bridge_sessions.values()))
    original_submit = service._submit_http_bridge_request_with_handoff
    injected_states = []
    if after_commit:
        _commit_before_refusal(service, monkeypatch)

    if refusal == "startup_cooldown":

        async def cooldown(_session):
            if after_commit:
                await asyncio.sleep(0.05)
            return 3.0

        monkeypatch.setattr(service, "_http_bridge_precreated_retry_cooldown_seconds", cooldown)

    async def inject(current, **kwargs):
        if after_commit:
            await asyncio.sleep(0.05)
        state = kwargs["request_state"]
        injected_states.append(state)
        if refusal == "cooldown":
            monkeypatch.setattr(service, "_http_bridge_precreated_retry_allowed", AsyncMock(return_value=False))
            monkeypatch.setattr(
                service, "_http_bridge_precreated_retry_block", AsyncMock(return_value=(3.0, "cooldown"))
            )
        elif refusal == "generation":
            state.verified_stale_anchor_replay = True
            state.verified_stale_anchor_retry_circuit_generation_captured = True
            state.verified_stale_anchor_retry_circuit_key = current.key
            state.verified_stale_anchor_retry_circuit_generation = (0, 0.0, 0, 0.0, 0, 0.0, 0.0)
            monkeypatch.setattr(service, "_claim_http_bridge_retry_circuit_generation", AsyncMock(return_value=False))
            monkeypatch.setattr(service, "_http_bridge_claim_miss_shows_remote_probe", AsyncMock(return_value=False))
        elif refusal == "retiring":
            current.upstream_control.retire_after_drain = True
        elif refusal in {"unregistered", "reconnect"}:
            current.closed = True
            if refusal == "unregistered":
                service._http_bridge_sessions.pop(current.key)
            monkeypatch.setattr(service, "_retry_http_bridge_request_on_fresh_upstream", AsyncMock(return_value=False))
        elif refusal == "lease_race":
            acquire_lease = service._load_balancer.acquire_account_lease

            async def close_after_lease(*args, **lease_kwargs):
                lease = await acquire_lease(*args, **lease_kwargs)
                current.closed = True
                return lease

            monkeypatch.setattr(service._load_balancer, "acquire_account_lease", close_after_lease)
        else:
            original_admit = service._acquire_request_state_response_create_admission

            async def close_after_admission(*args, **admission_kwargs):
                await original_admit(*args, **admission_kwargs)
                current.closed = True

            monkeypatch.setattr(service, "_acquire_request_state_response_create_admission", close_after_admission)
            monkeypatch.setattr(service, "_retry_http_bridge_request_on_fresh_upstream", AsyncMock(return_value=False))
        return await original_submit(current, **kwargs)

    monkeypatch.setattr(service, "_submit_http_bridge_request_with_handoff", inject)
    monkeypatch.setattr(proxy_api, "_HTTP_BRIDGE_STARTUP_ERROR_PROBE_SECONDS", 0.0 if after_commit else 0.5)
    sent = len(bridge_origin.frames)
    response = await asyncio.wait_for(
        post(
            {
                "model": "gpt-5.1",
                "input": [_user("next")],
                "previous_response_id": "resp_contract_1",
                "stream": True,
            },
        ),
        timeout=10,
    )
    assert response.text, "local refusal became an empty HTTP 200"
    timeout_refusal = refusal in {"cooldown", "generation", "startup_cooldown"}
    expected_code = "upstream_request_timeout" if timeout_refusal else "upstream_unavailable"
    if refusal == "startup_cooldown":
        expected_code = "bridge_eventless_timeout"
    if response.status_code == 200:
        terminals = [event for event in _events(response) if event["type"] == "response.failed"]
        assert len(terminals) == 1, response.text
        assert terminals[0]["response"]["error"]["code"] == expected_code
        assert response.text.rstrip().endswith("data: [DONE]")
    else:
        assert response.status_code == (503 if timeout_refusal else 502), response.text
        assert response.json()["error"]["code"] == expected_code
    if after_commit:
        assert response.status_code == 200
    assert "_codex_lb_synthetic_transport_failure" not in response.text
    if path == "/internal/bridge/responses":
        assert response.headers.get(HTTP_BRIDGE_LOCAL_PRE_DISPATCH_REFUSAL_HEADER) == "1"
    assert len(bridge_origin.frames) == sent
    assert len(injected_states) == (0 if refusal == "startup_cooldown" else 1)
    assert all(state.response_create_attempt_count == 0 for state in injected_states)
    assert not session.pending_requests
    assert session.queued_request_count == 0
    assert session.admission_waiter_count == 0
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    async with SessionLocal() as database:
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert len(reservations) == 2
        assert all(row.status in {"released", "finalized"} for row in reservations)
    await service._close_http_bridge_session(session)
    assert await service._load_balancer.account_pressure_snapshot(bridge_origin.owner_id) == (0, 0, 0.0)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("storage_failure", [None, "claim", "renew"])
async def test_model_transition_successor_converges_on_the_next_turn(
    async_client, app_instance, bridge_origin, monkeypatch, path, storage_failure
):
    alternate = await _import_account(async_client, "model-successor", "successor@example.invalid")
    created = await async_client.post(
        "/api/api-keys/",
        json={"name": "model-transition-contract", "assignedAccountIds": [bridge_origin.owner_id, alternate]},
    )
    assert created.status_code == 200, created.text
    key_id = created.json()["id"]
    monkeypatch.setitem(async_client.headers, "Authorization", f"Bearer {created.json()['key']}")
    token = "http_turn_model_transition_contract"
    headers = {"session_id": "model-transition-contract", "x-codex-turn-state": token}
    service = get_proxy_service_for_app(app_instance)
    initial_select = service._select_account_with_budget

    async def select_seed_owner(*args, **kwargs):
        kwargs["preferred_account_id"] = bridge_origin.owner_id
        kwargs["fallback_on_preferred_account_unavailable"] = False
        return await initial_select(*args, **kwargs)

    monkeypatch.setattr(service, "_select_account_with_budget", select_seed_owner)
    first_input = [_user("old model")]
    seed = await async_client.post(
        path, headers=headers, json={"model": "gpt-5.1", "input": first_input, "stream": True}
    )
    assert seed.status_code == 200, seed.text
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    parent = await service._durable_bridge.lookup_turn_state_target(turn_state=token, api_key_id=key_id)
    assert parent is not None and parent.account_id == bridge_origin.owner_id
    monkeypatch.setattr(service, "_select_account_with_budget", initial_select)
    async with SessionLocal() as database:
        await StickySessionsRepository(database).upsert(token, alternate, kind=StickySessionKind.CODEX_SESSION)
    selections = []
    actual_select = service._load_balancer.select_account

    async def capture_selection(*args, **kwargs):
        selection = await actual_select(*args, **kwargs)
        selections.append(selection)
        return selection

    monkeypatch.setattr(service._load_balancer, "select_account", capture_selection)
    if storage_failure == "claim":
        monkeypatch.setattr(
            service._durable_bridge,
            "claim_live_session",
            AsyncMock(
                side_effect=OperationalError(
                    "claim", {}, sqlite3.OperationalError("no such table: http_bridge_sessions")
                )
            ),
        )
    body = {"model": "gpt-5.2", "input": [_user("new model")], "stream": True}
    second = await asyncio.wait_for(async_client.post(path, headers=headers, json=body), timeout=10)
    if storage_failure == "claim":
        assert second.status_code == 502, second.text
        assert second.json()["error"]["code"] == "upstream_unavailable"
        assert len(bridge_origin.frames) == 1
        return
    assert second.status_code == 200, second.text
    assert _events(second)[-1]["type"] == "response.completed", second.text
    assert any(selection.error_code == "continuity_owner_conflict" for selection in selections)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    successor = await service._durable_bridge.lookup_turn_state_target(turn_state=token, api_key_id=key_id)
    assert successor is not None and successor.account_id == alternate
    assert successor.session_id != parent.session_id
    connections = bridge_origin.connections
    conflict_count = sum(selection.error_code == "continuity_owner_conflict" for selection in selections)
    body["input"] = [
        *body["input"],
        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "OK"}]},
        {"type": "reasoning", "id": "rs_owned", "encrypted_content": "opaque", "summary": []},
        _user("next turn"),
    ]
    if storage_failure == "renew":
        monkeypatch.setattr(
            service._durable_bridge, "renew_live_session", AsyncMock(side_effect=RuntimeError("renew unavailable"))
        )
    third = await asyncio.wait_for(async_client.post(path, headers=headers, json=body), timeout=10)
    if storage_failure == "renew":
        assert third.status_code == 502, third.text
        assert third.json()["error"]["code"] == "upstream_unavailable"
        assert len(bridge_origin.frames) == 2
        return
    assert third.status_code == 200, third.text
    assert _events(third)[-1]["type"] == "response.completed", third.text
    assert bridge_origin.connections == connections
    assert sum(selection.error_code == "continuity_owner_conflict" for selection in selections) == conflict_count
    final = await service._durable_bridge.lookup_turn_state_target(turn_state=token, api_key_id=key_id)
    assert final is not None and final.session_id == successor.session_id
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert len(bridge_origin.frames) == 3


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "after_commit"), [(path, False) for path in PATHS] + [("/backend-api/codex/responses", True)]
)
@pytest.mark.parametrize("refusal", ["parallel", "handoff", "owner", "ring"])
async def test_creation_refusal_sites_preserve_native_error(
    async_client, app_instance, bridge_origin, monkeypatch, path, refusal, after_commit
):
    token = "http_turn_creation_refusal"
    headers = {"session_id": "creation-refusal", "x-codex-turn-state": token, "User-Agent": "codex_exec/0.153.4"}

    async def post(body):
        body = {"instructions": "hi", **body}
        if path == "/backend-api/codex/responses":
            body.pop("stream", None)
        async with _client_reporting_committed_stream_failures(app_instance) as wire_client:
            wire_client.headers.update(async_client.headers)
            return await wire_client.post(path, headers=headers, json=body)

    seed = await post({"model": "gpt-5.1", "input": [_user("seed")], "stream": True})
    assert seed.status_code == 200, seed.text
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    session = next(iter(service._http_bridge_sessions.values()))
    original_create = service._get_or_create_http_bridge_session
    reached = []
    if after_commit:
        _commit_before_refusal(service, monkeypatch)

    async def inject(key, **kwargs):
        if after_commit:
            await asyncio.sleep(0.05)
        reached.append(refusal)
        if refusal == "parallel":
            bridge_helpers._http_bridge_parallel_fork_key(
                key=key,
                session=session,
                inflight_creation=False,
                incoming_turn_state=token,
                previous_response_id="resp_contract_1",
                request_model="incompatible-model",
                request_service_tier=None,
                request_scope_id="creation-contract",
                allow_model_fork=False,
                same_model_required=True,
            )
        elif refusal == "handoff":
            service._recover_http_bridge_incompatible_admission_handoff(
                key=key,
                existing=session,
                force_durable_takeover=False,
                original_request_unanchored=False,
                request_model="gpt-5.1",
                api_key=kwargs["api_key"],
                incoming_turn_state=token,
                previous_response_id="resp_contract_1",
                preferred_account_id=session.account.id,
                require_preferred_account=True,
                request_service_tier=None,
            )
        else:
            kwargs["durable_lookup"] = None
        return await original_create(key, **kwargs)

    if refusal in {"owner", "ring"}:
        await service._close_http_bridge_session(session)
        if refusal == "owner":
            monkeypatch.setattr(
                bridge_mixin,
                "_http_bridge_owner_instance",
                AsyncMock(side_effect=RuntimeError("owner metadata unavailable")),
            )
        else:
            monkeypatch.setattr(bridge_mixin, "_http_bridge_owner_instance", AsyncMock(return_value="local"))
            monkeypatch.setattr(
                bridge_mixin,
                "_active_http_bridge_instance_ring",
                AsyncMock(side_effect=RuntimeError("ring unavailable")),
            )
    monkeypatch.setattr(service, "_get_or_create_http_bridge_session", inject)
    monkeypatch.setattr(proxy_api, "_HTTP_BRIDGE_STARTUP_ERROR_PROBE_SECONDS", 0.0 if after_commit else 0.5)
    response = await asyncio.wait_for(
        post(
            {
                "model": "gpt-5.1",
                "input": [_user("next")],
                "previous_response_id": "resp_contract_1",
                "stream": True,
            },
        ),
        timeout=10,
    )
    expected_code = "stream_incomplete" if refusal == "parallel" else "upstream_unavailable"
    if after_commit:
        assert response.status_code == 200, response.text
        terminals = [event for event in _events(response) if event["type"] == "response.failed"]
        assert len(terminals) == 1 and terminals[0]["response"]["error"]["code"] == expected_code
        assert response.text.rstrip().endswith("data: [DONE]")
    else:
        assert response.status_code == (503 if refusal == "handoff" else 502), response.text
        assert response.json()["error"]["code"] == expected_code
    assert "_codex_lb_synthetic_transport_failure" not in response.text
    assert reached == [refusal]
    assert len(bridge_origin.frames) == 1
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    async with SessionLocal() as database:
        rows = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert len(rows) == 2 and all(row.status in {"released", "finalized"} for row in rows)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("failure_path", ["first_event", "later_event", "raised_error"])
@pytest.mark.parametrize("anchored", [False, True])
async def test_health_failure_after_real_settlement_preserves_one_terminal(
    async_client, app_instance, bridge_origin, monkeypatch, caplog, path, failure_path, anchored
):
    service = get_proxy_service_for_app(app_instance)
    seed = await async_client.post(path, json={"model": "gpt-5.1", "input": [_user("seed")], "stream": True})
    assert seed.status_code == 200, seed.text
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    settings = proxy_service.get_settings().model_copy(update={"upstream_stream_transport": "http"})
    dashboard = await proxy_service.get_settings_cache().get()
    dashboard.upstream_stream_transport = "http"
    monkeypatch.setattr(proxy_service, "get_settings", lambda: settings)
    monkeypatch.setattr(proxy_api, "get_settings", lambda: settings)
    attempts = []

    async def upstream(*args, **kwargs):
        if failure_path != "first_event":
            yield (
                'data: {"type":"response.created","response":{"id":"resp_health_contract","status":"in_progress"}}\n\n'
            )
        if failure_path == "raised_error":
            raise ProxyResponseError(
                429,
                {"error": {"code": "usage_limit_reached", "message": "quota exhausted", "type": "rate_limit_error"}},
            )
        yield (
            'data: {"type":"response.failed","response":{"id":"resp_health_contract","status":"failed",'
            '"error":{"code":"usage_limit_reached","message":"quota exhausted"}}}\n\n'
        )

    async def fail_health(account, error, code, **kwargs):
        async with SessionLocal() as database:
            rows = list(await database.scalars(select(ApiKeyUsageReservation)))
            assert len(rows) == 2
            assert all(row.status in {"finalized", "released"} for row in rows)
        attempts.append((account.id, code))
        raise RuntimeError("injected ordinary health persistence failure")

    monkeypatch.setattr(proxy_service, "core_stream_responses", upstream)
    monkeypatch.setattr(service, "_handle_stream_error", fail_health)
    response = await asyncio.wait_for(
        async_client.post(
            path,
            json={
                "model": "gpt-5.1",
                "input": [_user("next")],
                "stream": True,
                "previous_response_id": "resp_contract_1" if anchored else None,
            },
        ),
        timeout=10,
    )
    assert response.status_code == 200, response.text
    terminals = [
        event
        for event in _events(response)
        if event["type"] in {"response.completed", "response.incomplete", "response.failed", "error"}
    ]
    assert len(terminals) == 1 and terminals[0]["type"] == "response.failed", response.text
    expected_code = "previous_response_owner_unavailable" if anchored else "usage_limit_reached"
    assert terminals[0]["response"]["error"]["code"] == expected_code
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert attempts == [(bridge_origin.owner_id, "usage_limit_reached")], [
        (record.message, str(record.exc_info[1])) for record in caplog.records if record.exc_info is not None
    ]
    health_logs = [
        record
        for record in caplog.records
        if record.exc_info is not None and str(record.exc_info[1]) == "injected ordinary health persistence failure"
    ]
    assert len(health_logs) == 1 and "health" in health_logs[0].message
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    async with SessionLocal() as database:
        logs = list(await database.scalars(select(RequestLog)))
        assert any(row.error_code == expected_code for row in logs)
    assert len(bridge_origin.frames) == 1
