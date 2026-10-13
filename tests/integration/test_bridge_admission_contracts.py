from __future__ import annotations

import asyncio
import json
from contextlib import suppress

import pytest
import pytest_asyncio
from sqlalchemy import select, update

from app.db.models import (
    ApiKey,
    ApiKeyLimit,
    ApiKeyUsageReservation,
    ApiKeyUsageReservationItem,
    HttpBridgeOperationRecord,
)
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy._service.api_key_usage import _estimated_lease_tokens_from_request_usage_budget
from tests.integration import test_http_responses_bridge as bridge

pytestmark = pytest.mark.integration
PATHS = ["/backend-api/codex/responses", "/backend-api/codex/responses/", "/v1/responses", "/v1/responses/"]


@pytest_asyncio.fixture
async def bridge_transport(async_client, app_instance, monkeypatch):
    dashboard = bridge._make_dashboard_settings()
    dashboard.api_key_auth_enabled = True
    bridge._install_proxy_settings(
        monkeypatch, app_settings=bridge._make_app_settings(enabled=True), dashboard_settings=dashboard
    )
    account_id = await bridge._import_account(async_client, "admission-owner", "admission-owner@example.com")
    account = await bridge._get_account(account_id)
    upstream = bridge._FakeBridgeUpstreamWebSocket("resp_admission")
    bridge._install_bridge_account_upstream(monkeypatch, account=account, upstream=upstream)
    service = get_proxy_service_for_app(app_instance)
    try:
        yield service, upstream
    finally:
        await service.close_all_http_bridge_sessions()


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("outcome", ["allowed", "quota", "auth"])
async def test_late_hard_turn_anchor_reconciles_real_quota_before_send(
    async_client, bridge_transport, monkeypatch, path: str, outcome: str
) -> None:
    service, upstream = bridge_transport
    key_response = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "late-anchor-limit",
            "limits": [
                {
                    "limitType": "total_tokens",
                    "limitWindow": "weekly",
                    "maxValue": 5000 if outcome == "quota" else 20000,
                }
            ],
        },
    )
    assert key_response.status_code == 200, key_response.text
    key_id = key_response.json()["id"]
    enable = await async_client.put(
        "/api/settings",
        json={
            "stickyThreadsEnabled": False,
            "preferEarlierResetAccounts": False,
            "totpRequiredOnLogin": False,
            "apiKeyAuthEnabled": True,
        },
    )
    assert enable.status_code == 200, enable.text
    headers = {"Authorization": f"Bearer {key_response.json()['key']}"}
    body = {"model": "gpt-5.1", "instructions": "", "input": [{"role": "user", "content": "Continue"}], "stream": True}
    first = await async_client.post(path, headers=headers, json=body)
    assert first.status_code == 200 and "response.completed" in first.text
    async with SessionLocal() as session:
        completed = (await session.scalars(select(HttpBridgeOperationRecord))).one()
        assert completed.state == "completed"
        parent_id = completed.response_id
    assert parent_id

    # Model the durable-completion race at the real submit path. Other ledger,
    # admission, reservation, dispatch and settlement code remains production.
    original_lookup = service._durable_bridge.get_operation_by_fingerprint
    inject_prior_completion = True

    async def lookup(**kwargs):
        nonlocal inject_prior_completion
        if inject_prior_completion:
            inject_prior_completion = False
            return completed
        return await original_lookup(**kwargs)

    monkeypatch.setattr(service._durable_bridge, "get_operation_by_fingerprint", lookup)
    prepare = service._prepare_response_bridge_request_state

    def prepare_hard_turn(*args, **kwargs):
        state, text = prepare(*args, **kwargs)
        state.hard_continuity_anchor = True
        return state, text

    monkeypatch.setattr(service, "_prepare_response_bridge_request_state", prepare_hard_turn)
    reconcile = service._reconcile_websocket_request_state_reservation
    local_estimates = []

    async def observe_reconciliation(state, **kwargs):
        if outcome == "auth":
            async with SessionLocal() as session:
                await session.execute(update(ApiKey).where(ApiKey.id == key_id).values(is_active=False))
                await session.commit()
        await reconcile(state, **kwargs)
        local_estimates.append(_estimated_lease_tokens_from_request_usage_budget(state.request_usage_budget))

    monkeypatch.setattr(service, "_reconcile_websocket_request_state_reservation", observe_reconciliation)
    send = upstream.send_text
    persisted_budgets = []

    async def observe_send(text):
        assert json.loads(text)["previous_response_id"] == parent_id
        async with SessionLocal() as session:
            reservation = (
                await session.scalars(
                    select(ApiKeyUsageReservation).where(
                        ApiKeyUsageReservation.api_key_id == key_id, ApiKeyUsageReservation.status == "reserved"
                    )
                )
            ).one()
            item = (
                await session.scalars(
                    select(ApiKeyUsageReservationItem).where(
                        ApiKeyUsageReservationItem.reservation_id == reservation.id
                    )
                )
            ).one()
            persisted_budgets.append(item.reserved_delta)
        await send(text)

    monkeypatch.setattr(upstream, "send_text", observe_send)
    second = await async_client.post(path, headers=headers, json=body)
    assert not inject_prior_completion
    if outcome != "allowed":
        assert second.status_code == (429 if outcome == "quota" else 401), second.text
        assert second.json()["error"]["code"] == ("rate_limit_exceeded" if outcome == "quota" else "invalid_api_key")
        assert len(upstream.sent_text) == 1
        assert not persisted_budgets and not local_estimates
    else:
        assert second.status_code == 200 and "response.completed" in second.text, second.text
        assert len(upstream.sent_text) == 2
        assert persisted_budgets == local_estimates == [10240]
    async with SessionLocal() as session:
        reservations = (
            await session.scalars(select(ApiKeyUsageReservation).where(ApiKeyUsageReservation.api_key_id == key_id))
        ).all()
        assert len(reservations) == 2
        assert all(reservation.status != "reserved" for reservation in reservations)
        limit = (await session.scalars(select(ApiKeyLimit).where(ApiKeyLimit.api_key_id == key_id))).one()
        assert limit.current_value == (52 if outcome == "allowed" else 26)


@pytest.mark.parametrize("path", PATHS)
async def test_public_retry_recovers_stale_closed_handoff(
    async_client, bridge_transport, monkeypatch, path: str
) -> None:
    service, upstream = bridge_transport
    headers = {"x-codex-session-id": "closed-admission"}
    body = {"model": "gpt-5.1", "instructions": "", "input": "Hello", "stream": True}
    first = await async_client.post(path, headers=headers, json=body)
    assert first.status_code == 200 and "response.completed" in first.text
    async with service._http_bridge_lock:
        key, old = next(iter(service._http_bridge_sessions.items()))
        old.closed = True
        old.admission_waiter_count = 1
        old.request_model = "gpt-5.4"
        old.upstream_control.retire_after_drain = True
    replacement_upstream = bridge._FakeBridgeUpstreamWebSocket("resp_after_handoff")

    async def connect(*args, **kwargs):
        return replacement_upstream

    monkeypatch.setattr(bridge.proxy_module, "connect_responses_websocket", connect)
    try:
        replacement = await async_client.post(path, headers=headers, json=body)
        assert replacement.status_code == 200 and "resp_after_handoff_1" in replacement.text, replacement.text
        assert service._http_bridge_sessions[key] is not old
        assert len(upstream.sent_text) == len(replacement_upstream.sent_text) == 1
        assert old.admission_waiter_count == 1
    finally:
        old.admission_waiter_count = 0
        await service._close_http_bridge_session(old)


@pytest.mark.parametrize("path", PATHS)
async def test_failed_creator_releases_public_request_slot_for_replacement(
    async_client, bridge_transport, monkeypatch, path: str
) -> None:
    service, upstream = bridge_transport
    dashboard = bridge._make_dashboard_settings()
    bridge._install_proxy_settings(
        monkeypatch,
        app_settings=bridge._make_app_settings(enabled=True),
        dashboard_settings=dashboard,
        admission_wait_timeout_seconds=5,
    )
    create = service._create_http_bridge_session
    started = asyncio.Event()
    cancelled = asyncio.Event()
    attempts = 0

    async def stall_first(*args, **kwargs):
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            started.set()
            try:
                await asyncio.Future()
            finally:
                cancelled.set()
        return await create(*args, **kwargs)

    monkeypatch.setattr(service, "_create_http_bridge_session", stall_first)
    body = {"model": "gpt-5.1", "instructions": "", "input": "Hello", "stream": True, "prompt_cache_key": "creator"}
    predecessor = asyncio.create_task(async_client.post(path, json=body))
    try:
        await asyncio.wait_for(started.wait(), timeout=5)
        async with service._http_bridge_lock:
            key, future = next(iter(service._http_bridge_inflight_sessions.items()))
        assert await service._fail_http_bridge_inflight_session_creation(key, future, RuntimeError("creation refused"))
        await asyncio.wait_for(cancelled.wait(), timeout=5)
        with suppress(asyncio.CancelledError):
            await predecessor
        replacement = await async_client.post(path, json=body)
        assert replacement.status_code == 200 and "response.completed" in replacement.text, replacement.text
        assert attempts == 2
        assert len(upstream.sent_text) == 1
        assert not service._http_bridge_inflight_sessions
        async with SessionLocal() as session:
            operations = (await session.scalars(select(HttpBridgeOperationRecord))).all()
            assert len(operations) == 1 and operations[0].state == "completed"
    finally:
        predecessor.cancel()
        await asyncio.gather(predecessor, return_exceptions=True)


@pytest.mark.parametrize("spool_format", ["rows_v1", "chunks_v2"])
async def test_public_stream_drains_real_transcript_burst_before_terminal(
    async_client, bridge_transport, monkeypatch, spool_format: str
) -> None:
    service, upstream = bridge_transport
    batcher = service._http_bridge_operation_event_batcher
    batcher._spool_format = spool_format
    batcher._batch_size = 32
    batcher._flush_interval_seconds = 60
    drained = asyncio.Event()
    queued = asyncio.Event()
    enqueue_count = 0
    batches = []
    terminal = None
    send = upstream.send_text

    async def send_burst(text):
        nonlocal terminal
        await send(text)
        created = upstream._messages.get_nowait()
        terminal = upstream._messages.get_nowait()
        upstream._messages.put_nowait(created)
        for index in range(319):
            upstream._messages.put_nowait(
                bridge._FakeUpstreamMessage(
                    "text", text=json.dumps({"type": "response.output_text.delta", "delta": f"part-{index}"})
                )
            )

    monkeypatch.setattr(upstream, "send_text", send_burst)
    enqueue = batcher.enqueue

    async def observe_enqueue(**kwargs):
        nonlocal enqueue_count
        await enqueue(**kwargs)
        enqueue_count += 1
        if enqueue_count == 320:
            queued.set()

    monkeypatch.setattr(batcher, "enqueue", observe_enqueue)
    method = "append_operation_events" if spool_format == "rows_v1" else "append_operation_event_chunk"
    append = getattr(service._durable_bridge, method)

    async def observe_append(**kwargs):
        await queued.wait()
        result = await append(**kwargs)
        assert result
        batches.append(len(kwargs["events"]))
        if sum(batches) == 320:
            drained.set()
        return result

    monkeypatch.setattr(service._durable_bridge, method, observe_append)
    request = asyncio.create_task(
        async_client.post(
            "/backend-api/codex/responses",
            json={"model": "gpt-5.1", "instructions": "", "input": "Burst", "stream": True},
        )
    )
    try:
        await asyncio.wait_for(drained.wait(), timeout=10)
        assert terminal is not None and not request.done()
        assert sum(batches) == 320 and 10 <= len(batches) <= 11
        assert all(0 < count <= 32 for count in batches)
        upstream._messages.put_nowait(terminal)
        response = await request
        assert response.status_code == 200 and "response.completed" in response.text
        async with SessionLocal() as session:
            operation = (await session.scalars(select(HttpBridgeOperationRecord))).one()
            assert operation.state == "completed" and operation.event_spool_complete
        events = await service._durable_bridge.get_operation_events(operation_id=operation.operation_id)
        payloads = [json.loads(event.split("data: ", 1)[1]) for event in events]
        assert len(payloads) == 321
        assert payloads[0]["type"] == "response.created"
        assert [event["delta"] for event in payloads[1:-1]] == [f"part-{index}" for index in range(319)]
        assert payloads[-1]["type"] == "response.completed"
    finally:
        request.cancel()
        await asyncio.gather(request, return_exceptions=True)
