from __future__ import annotations

import asyncio
import json
import time
from contextlib import nullcontext
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.clients.proxy_websocket import UpstreamWebSocketMessage
from app.core.utils.sse import parse_sse_data_json
from app.modules.proxy import service as proxy_service
from app.modules.proxy._service.http_bridge import request_submit, retry_circuit
from app.modules.proxy._service.support import _HTTPBridgeResponseCreateAttempt
from app.modules.proxy.durable_bridge_coordinator import DurableBridgeSessionCoordinator
from tests.simulation.virtual_time import VirtualClock
from tests.unit.test_durable_bridge_sessions import async_session_factory as _session_factory_fixture
from tests.unit.test_proxy_http_bridge import _make_bridge_session, _make_eventless_http_bridge_owner

pytestmark = pytest.mark.unit
async_session_factory = _session_factory_fixture


@pytest.fixture
async def coordinator(async_session_factory):
    return DurableBridgeSessionCoordinator(async_session_factory)


@pytest.mark.asyncio
async def test_claim_receipt_cannot_be_replaced_by_a_successor_after_commit(monkeypatch, coordinator):
    identity = {
        "session_key_kind": "session_header",
        "session_key_value": "transaction-claim-receipt",
        "api_key_id": None,
    }
    epoch = time.time()
    await coordinator.persist_retry_circuit(
        **identity, consecutive_failures=2, cooldown_until_epoch=0.0, last_detail="clean_close", updated_at_epoch=epoch
    )
    commit = AsyncSession.commit
    replace_after_commit = True

    async def commit_and_claim_successor(session):
        nonlocal replace_after_commit
        await commit(session)
        if replace_after_commit:
            replace_after_commit = False
            successor = await coordinator.claim_retry_circuit_generation(
                **identity,
                expected_updated_at_epoch=epoch,
                expected_admission_generation=1,
                expected_consecutive_failures=2,
                expected_cooldown_until_epoch=0.0,
            )
            assert successor is not None
            assert successor.admission_generation == 2

    monkeypatch.setattr(AsyncSession, "commit", commit_and_claim_successor)
    receipt = await coordinator.claim_retry_circuit_generation(
        **identity,
        expected_updated_at_epoch=epoch,
        expected_admission_generation=0,
        expected_consecutive_failures=2,
        expected_cooldown_until_epoch=0.0,
    )
    assert receipt is not None
    assert receipt.admission_generation == 1
    assert not await coordinator.release_retry_circuit_claim(
        **identity,
        expected_updated_at_epoch=receipt.updated_at_epoch,
        expected_admission_generation=receipt.admission_generation,
    )
    stored = await coordinator.lookup_retry_circuit(**identity)
    assert stored is not None and stored.admission_generation == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("outcome", [True, False, RuntimeError("database unavailable")])
async def test_durable_release_preserves_replacement_local_probe(monkeypatch, outcome):
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    session = _make_bridge_session(key_value="replacement-local-probe")
    state = retry_circuit._HTTPBridgeRetryCircuitState(
        consecutive_failures=3,
        cooldown_until=17.0,
        half_open_until=time.monotonic() + 300.0,
        persisted_updated_at_epoch=20.0,
        persisted_admission_generation=4,
    )
    service._http_bridge_retry_circuits[session.key] = state
    lease = state.half_open_until
    release = AsyncMock(side_effect=outcome) if isinstance(outcome, Exception) else AsyncMock(return_value=outcome)
    monkeypatch.setattr(service._durable_bridge, "release_retry_circuit_claim", release)

    result = await service._release_http_bridge_retry_circuit_claim(
        key=session.key, generation=(1, 10.0, 2, 0.0, 2, 0.0, 0.0)
    )

    assert result is (outcome is True)
    assert state.half_open_until == lease
    assert state.cooldown_until == 17.0
    assert state.persisted_admission_generation == 4


@pytest.mark.asyncio
@pytest.mark.parametrize("cancel_release", [False, True])
@pytest.mark.parametrize("existing_row", [False, True, "local_only"])
async def test_cancelled_submit_recovers_committed_claim_receipt(
    monkeypatch, coordinator, async_client, cancel_release, existing_row
):
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    service._durable_bridge = coordinator
    session = _make_bridge_session(key_value="claim-cancellation-source")
    service._http_bridge_sessions[session.key] = session
    if existing_row is True:
        await coordinator.persist_retry_circuit(
            session_key_kind=session.key.affinity_kind,
            session_key_value=session.key.affinity_key,
            api_key_id=None,
            consecutive_failures=2,
            cooldown_until_epoch=0.0,
            last_detail="clean_close",
            updated_at_epoch=time.time(),
        )
    elif existing_row == "local_only":
        service._http_bridge_retry_circuits[session.key] = retry_circuit._HTTPBridgeRetryCircuitState(
            consecutive_failures=2,
            last_touched_monotonic=time.monotonic(),
            last_failure_monotonic=time.monotonic(),
        )
    assert await service._load_http_bridge_retry_circuit(session)
    captured, generation = await service._http_bridge_retry_circuit_generation(session)
    assert captured
    request = _make_eventless_http_bridge_owner(request_id="cancelled-claim-owner")
    request.previous_response_id = None
    request.proxy_injected_previous_response_id = False
    request.skip_request_log = True
    request.started_at = time.monotonic()
    request.response_create_gate_acquired = False
    request.response_create_gate = None
    request.response_create_sent_at = None
    session.upstream.send_text = AsyncMock()
    request.verified_stale_anchor_replay = True
    request.verified_stale_anchor_retry_circuit_generation_captured = True
    request.verified_stale_anchor_retry_circuit_key = session.key
    request.verified_stale_anchor_retry_circuit_generation = generation
    committed = asyncio.Event()
    deliver = asyncio.Event()
    released = asyncio.Event()
    return_release = asyncio.Event()
    claim = coordinator.claim_retry_circuit_generation

    async def delayed_receipt(**kwargs):
        receipt = await claim(**kwargs)
        assert receipt is not None
        committed.set()
        await deliver.wait()
        return receipt

    monkeypatch.setattr(coordinator, "claim_retry_circuit_generation", delayed_receipt)
    if cancel_release:
        release = coordinator.release_retry_circuit_claim

        async def delayed_release(**kwargs):
            result = await release(**kwargs)
            released.set()
            await return_release.wait()
            return result

        monkeypatch.setattr(coordinator, "release_retry_circuit_claim", delayed_release)
    task = asyncio.create_task(
        service._submit_http_bridge_request(
            session,
            request_state=request,
            text_data='{"type":"response.create","model":"gpt-5.4","input":"hello"}',
            queue_limit=8,
        )
    )
    try:
        await asyncio.wait_for(committed.wait(), timeout=3)
        task.cancel()
        await asyncio.sleep(0)
        deliver.set()
        if cancel_release:
            await asyncio.wait_for(released.wait(), timeout=3)
            task.cancel()
            await asyncio.sleep(0)
            task.cancel()
            return_release.set()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=3)
    finally:
        deliver.set()
        return_release.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    persisted = await coordinator.lookup_retry_circuit(
        session_key_kind=session.key.affinity_kind, session_key_value=session.key.affinity_key, api_key_id=None
    )
    assert persisted is not None
    assert persisted.admission_generation == (generation[0] if generation is not None else 0)
    assert persisted.consecutive_failures == (2 if existing_row is True else 0)
    assert request.response_create_attempt_count == 0
    assert request.claimed_durable_circuit_key is None
    assert not session.pending_requests
    session.upstream.send_text.assert_not_awaited()


@pytest.mark.asyncio
@pytest.mark.parametrize("cooldown", [0.0, -10.0, "elapsed", "missing"])
async def test_real_durable_elapsed_cooldown_allows_repeated_admission(coordinator, cooldown):
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    service._durable_bridge = coordinator
    session = _make_bridge_session(key_value="durable-elapsed-cooldown")
    if cooldown != "missing":
        await coordinator.persist_retry_circuit(
            session_key_kind=session.key.affinity_kind,
            session_key_value=session.key.affinity_key,
            api_key_id=None,
            consecutive_failures=3,
            cooldown_until_epoch=time.time() - 30.0 if cooldown == "elapsed" else cooldown,
            last_detail="clean_close",
            updated_at_epoch=time.time(),
        )
    for _ in range(3):
        assert await service._http_bridge_precreated_retry_allowed(session)
    state = service._http_bridge_retry_circuits.get(session.key)
    assert state is None or (state.cooldown_until == 0.0 and state.half_open_until == 0.0)


@pytest.mark.asyncio
async def test_cancelled_claim_cannot_wait_forever_on_local_key_lock(monkeypatch, coordinator, async_client):
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    service._durable_bridge = coordinator
    session = _make_bridge_session(key_value="claim-key-lock-timeout")
    service._http_bridge_sessions[session.key] = session
    session.upstream.send_text = AsyncMock()
    request = _make_eventless_http_bridge_owner(request_id="bounded-key-lock-owner")
    request.started_at = time.monotonic()
    request.skip_request_log = True
    request.response_create_gate_acquired = False
    request.response_create_gate = None
    request.response_create_sent_at = None
    request.verified_stale_anchor_replay = True
    request.verified_stale_anchor_retry_circuit_generation_captured = True
    request.verified_stale_anchor_retry_circuit_key = session.key
    request.verified_stale_anchor_retry_circuit_generation = None
    key_lock = await service._acquire_http_bridge_retry_circuit_key_lock(session.key)
    entered = asyncio.Event()
    claim = service._claim_http_bridge_retry_circuit_generation

    async def observe_claim(**kwargs):
        entered.set()
        return await claim(**kwargs)

    monkeypatch.setattr(service, "_claim_http_bridge_retry_circuit_generation", observe_claim)
    monkeypatch.setattr(request_submit, "_HTTP_BRIDGE_RETRY_CIRCUIT_CLAIM_TIMEOUT_SECONDS", 0.05)
    task = asyncio.create_task(
        service._submit_http_bridge_request(
            session,
            request_state=request,
            text_data='{"type":"response.create","model":"gpt-5.4","input":"hello"}',
            queue_limit=8,
        )
    )
    try:
        await asyncio.wait_for(entered.wait(), timeout=3)
        task.cancel()
        with pytest.raises((asyncio.CancelledError, proxy_service.ProxyResponseError, TimeoutError)):
            await asyncio.wait_for(task, timeout=1)
        assert task.done()
        assert key_lock.locked()
    finally:
        key_lock.release()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
    assert (
        await coordinator.lookup_retry_circuit(
            session_key_kind=session.key.affinity_kind, session_key_value=session.key.affinity_key, api_key_id=None
        )
        is None
    )
    assert request.response_create_attempt_count == 0
    session.upstream.send_text.assert_not_awaited()


@pytest.mark.asyncio
async def test_real_cooldown_expiry_admits_one_local_probe_and_preserves_it_on_reload(coordinator):
    clock = VirtualClock(epoch_value=1000.0)
    service = proxy_service.ProxyService(cast(Any, nullcontext()), clock=clock)
    service._durable_bridge = coordinator
    session = _make_bridge_session(key_value="real-active-local-probe")
    await coordinator.persist_retry_circuit(
        session_key_kind=session.key.affinity_kind,
        session_key_value=session.key.affinity_key,
        api_key_id=None,
        consecutive_failures=2,
        cooldown_until_epoch=1010.0,
        last_detail="clean_close",
        updated_at_epoch=1000.0,
    )
    assert not await service._http_bridge_precreated_retry_allowed(session)
    clock.advance(11.0)
    leases = []
    assert await service._http_bridge_precreated_retry_allowed(session, claimed_lease_out=leases)
    assert len(leases) == 1
    for _ in range(3):
        assert not await service._http_bridge_precreated_retry_allowed(session)
    state = service._http_bridge_retry_circuits[session.key]
    assert state.cooldown_until == 0.0
    assert state.half_open_until == leases[0]


@pytest.mark.asyncio
@pytest.mark.parametrize("interpreted", [False, True])
@pytest.mark.parametrize(
    "case",
    [
        "reason",
        "explicit_transport",
        "explicit_other",
        "unknown",
        "missing",
        "prewarm",
        "skip_log",
        "observed",
        "safe_replay",
        "soft",
        "disarmed",
        "reasoning",
    ],
)
async def test_incomplete_accounting_raw_and_interpreted_with_real_persistence(coordinator, interpreted, case):
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    service._durable_bridge = coordinator
    key = proxy_service._HTTPBridgeSessionKey(
        "prompt_cache_key" if case == "soft" else "session_header", "reason-case", None
    )
    session = _make_bridge_session(key=key)
    request = _make_eventless_http_bridge_owner()
    request.response_create_attempt = _HTTPBridgeResponseCreateAttempt(
        ordinal=1, disarmed=case == "disarmed", non_terminal_response_observed=case == "reasoning"
    )
    attempt = request.response_create_attempt
    if case == "prewarm":
        request.request_kind = "prewarm"
    if case == "skip_log":
        request.skip_request_log = True
    if case == "observed":
        request.response_event_count = 1
    if case == "safe_replay":
        request.fresh_upstream_request_is_retry_safe = True
        request.fresh_upstream_request_text = '{"type":"response.create","input":"full history"}'
    response = {"id": "resp_reason_only", "status": "incomplete"}
    if case != "missing":
        response["incomplete_details"] = {"reason": "max_output_tokens" if case == "unknown" else "stream_incomplete"}
    if case.startswith("explicit_"):
        response["error"] = {
            "type": "server_error" if case == "explicit_transport" else "invalid_request_error",
            "code": "stream_incomplete" if case == "explicit_transport" else "invalid_request_error",
            "message": "upstream terminal",
        }
    payload = {"type": "response.incomplete", "response": response}
    text = json.dumps(payload)
    session.pending_requests.append(request)
    message = (
        UpstreamWebSocketMessage(
            kind="text", text=text, responses_interpreted=True, event_type="response.incomplete", payload=payload
        )
        if interpreted
        else None
    )

    await service._process_http_bridge_upstream_text(session, text, message=message)

    persisted = await coordinator.lookup_retry_circuit(
        session_key_kind=key.affinity_kind, session_key_value=key.affinity_key, api_key_id=None
    )
    eligible = case in {"reason", "explicit_transport"}
    assert (persisted is not None) is eligible
    if eligible:
        assert persisted.consecutive_failures == 1
        assert (
            await service._record_http_bridge_retry_circuit_failure(
                session, detail="stream_incomplete", attempt=attempt, terminal_pre_response_frame=True
            )
            == 1
        )
        again = await coordinator.lookup_retry_circuit(
            session_key_kind=key.affinity_kind, session_key_value=key.affinity_key, api_key_id=None
        )
        assert again == persisted
    assert request.event_queue is not None
    events = []
    while not request.event_queue.empty():
        block = request.event_queue.get_nowait()
        if block is not None:
            events.append(parse_sse_data_json(block))
    assert events[-1] == payload
