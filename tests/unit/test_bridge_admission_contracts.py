from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ProxyRateLimitError
from app.modules.api_keys.service import (
    API_KEY_USAGE_RESERVATION_DEFAULT_INPUT_TOKENS,
    API_KEY_USAGE_RESERVATION_DEFAULT_OUTPUT_TOKENS,
    ApiKeyRateLimitExceededError,
    ApiKeyRequestUsageBudget,
    ApiKeyUsageReservationData,
)
from app.modules.proxy import service as proxy_service
from app.modules.proxy._service import api_key_usage
from app.modules.proxy.http_bridge_event_batcher import HttpBridgeOperationEventBatcher


@pytest.mark.asyncio
@pytest.mark.parametrize("waiter_done", [False, True])
@pytest.mark.parametrize("cancel_error", [False, True])
async def test_failed_creation_cancels_owned_creator_even_after_waiter_completion(
    waiter_done: bool, cancel_error: bool
) -> None:
    service = proxy_service.ProxyService(cast(Any, SimpleNamespace()))
    key = proxy_service._HTTPBridgeSessionKey("session_header", "failed-creator", None)
    future = asyncio.get_running_loop().create_future()
    started = asyncio.Event()
    cancelled = asyncio.Event()

    async def create() -> None:
        started.set()
        try:
            await asyncio.Future()
        finally:
            cancelled.set()

    creator = asyncio.create_task(create())
    setattr(future, "_creator_task", creator)
    service._http_bridge_inflight_sessions[key] = future
    await started.wait()
    if waiter_done:
        future.set_result(None)
    try:
        exc = asyncio.CancelledError() if cancel_error else RuntimeError("creation failed")
        assert await service._fail_http_bridge_inflight_session_creation(key, future, exc)
        assert key not in service._http_bridge_inflight_sessions
        assert creator.cancelling() > 0
        await asyncio.wait_for(cancelled.wait(), timeout=5)
        assert future.done()
        if not waiter_done:
            assert future.cancelled() is cancel_error
            if not cancel_error:
                with pytest.raises(RuntimeError, match="creation failed"):
                    future.result()
    finally:
        creator.cancel()
        await asyncio.gather(creator, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("protected", ["replacement", "handoff", "self"])
async def test_failed_creation_preserves_other_task_ownership(protected: str) -> None:
    service = proxy_service.ProxyService(cast(Any, SimpleNamespace()))
    key = proxy_service._HTTPBridgeSessionKey("session_header", "protected-creator", None)
    future = asyncio.get_running_loop().create_future()
    creator = asyncio.create_task(asyncio.Event().wait())
    setattr(future, "_creator_task", asyncio.current_task() if protected == "self" else creator)
    replacement = asyncio.get_running_loop().create_future()
    service._http_bridge_inflight_sessions[key] = replacement if protected == "replacement" else future
    if protected == "handoff":
        setattr(future, "_http_bridge_handoff", True)
    current = asyncio.current_task()
    assert current is not None
    previous_cancels = current.cancelling()
    try:
        result = await service._fail_http_bridge_inflight_session_creation(key, future, RuntimeError("failed"))
        assert result is (protected == "self")
        assert creator.cancelling() == 0
        assert current.cancelling() == previous_cancels
        if protected != "self":
            assert key in service._http_bridge_inflight_sessions
            assert not future.done()
    finally:
        creator.cancel()
        await asyncio.gather(creator, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("refused", [False, True])
@pytest.mark.parametrize("default_budget", [False, True])
async def test_late_anchor_reconciliation_retains_budget_for_next_lease(
    monkeypatch: pytest.MonkeyPatch, refused: bool, default_budget: bool
) -> None:
    api_service = SimpleNamespace(reconcile_usage_reservation=AsyncMock())
    if refused:
        api_service.reconcile_usage_reservation.side_effect = ApiKeyRateLimitExceededError(
            message="anchored quota exceeds limit", reset_at=datetime(2030, 1, 1, tzinfo=timezone.utc)
        )

    @asynccontextmanager
    async def repos():
        yield SimpleNamespace(api_keys=SimpleNamespace())

    monkeypatch.setattr(api_key_usage, "_service_api_keys_service", lambda: lambda repo: api_service)
    service = proxy_service.ProxyService(repo_factory=cast(Any, repos))
    initial = ApiKeyRequestUsageBudget(input_tokens=108, output_tokens=None)
    opaque = ApiKeyRequestUsageBudget(input_tokens=None, output_tokens=None)
    supplied_budget = None if default_budget else opaque
    state = proxy_service._WebSocketRequestState(
        request_id="late-anchor",
        model="gpt-6-astra",
        service_tier=None,
        reasoning_effort="max",
        api_key_reservation=ApiKeyUsageReservationData(reservation_id="reservation", key_id="key", model="gpt-6-astra"),
        started_at=0,
        request_usage_budget=initial,
    )
    if refused:
        with pytest.raises(ProxyRateLimitError, match="anchored quota exceeds limit"):
            await service._reconcile_websocket_request_state_reservation(state, request_usage_budget=supplied_budget)
        assert state.request_usage_budget is initial
    else:
        await service._reconcile_websocket_request_state_reservation(state, request_usage_budget=supplied_budget)
        assert state.request_usage_budget == opaque
        assert api_key_usage._estimated_lease_tokens_from_request_usage_budget(state.request_usage_budget) == (
            API_KEY_USAGE_RESERVATION_DEFAULT_INPUT_TOKENS + API_KEY_USAGE_RESERVATION_DEFAULT_OUTPUT_TOKENS
        )
    api_service.reconcile_usage_reservation.assert_awaited_once_with(
        "reservation", request_model="gpt-6-astra", request_service_tier=None, request_usage_budget=supplied_budget
    )


class _BacklogWriter:
    def __init__(self, *, fail_first_operation: bool) -> None:
        self.fail_first_operation = fail_first_operation
        self.batches: list[tuple[str, list[str]]] = []
        self.drained = asyncio.Event()

    async def append_operation_events(self, *, events, max_bytes: int) -> bool:
        del max_bytes
        operation = events[0].operation_id
        self.batches.append((operation, [event.event_text for event in events]))
        if operation == "b" and self.batches[-1][1][-1] == "b-5":
            self.drained.set()
        return not (self.fail_first_operation and operation == "a")

    append_operation_event_chunk = append_operation_events


@pytest.mark.asyncio
@pytest.mark.parametrize("spool_format", ["rows_v1", "chunks_v2"])
@pytest.mark.parametrize("fail_first_operation", [False, True])
async def test_backlog_passes_are_fair_and_do_not_wait_for_interval(
    spool_format: str, fail_first_operation: bool
) -> None:
    writer = _BacklogWriter(fail_first_operation=fail_first_operation)
    batcher = HttpBridgeOperationEventBatcher(
        writer, max_bytes=1024 * 1024, batch_size=2, flush_interval_seconds=60, spool_format=spool_format
    )
    try:
        for operation in ("a", "b"):
            for index in range(6):
                await batcher.enqueue(
                    operation_id=operation,
                    session_id="session",
                    instance_id="instance",
                    owner_epoch=1,
                    event_text=f"{operation}-{index}",
                )
        await asyncio.wait_for(writer.drained.wait(), timeout=5)
        expected_order = ["a", "b", "b", "b"] if fail_first_operation else ["a", "b", "a", "b", "a", "b"]
        assert [operation for operation, _ in writer.batches] == expected_order
        assert all(len(events) == 2 for _, events in writer.batches)
        assert [event for operation, events in writer.batches if operation == "b" for event in events] == [
            f"b-{index}" for index in range(6)
        ]
    finally:
        await batcher.close()
