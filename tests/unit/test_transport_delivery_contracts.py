from __future__ import annotations

import asyncio
import gc
from types import SimpleNamespace

import pytest

from app.modules.proxy._service.http_bridge import queues
from app.modules.proxy._service.http_bridge.queues import _HTTPBridgeEventQueue
from app.modules.proxy._service.http_bridge.upstream_events import _enqueue_http_bridge_downstream_event

pytestmark = pytest.mark.unit


@pytest.fixture
def small_budget(monkeypatch: pytest.MonkeyPatch) -> None:
    gc.collect()
    monkeypatch.setattr(queues, "_HTTP_BRIDGE_STREAM_PROCESS_BYTES_LIMIT", 10, raising=False)


def test_multiple_queues_share_the_live_payload_budget(small_budget: None) -> None:
    first = _HTTPBridgeEventQueue()
    second = _HTTPBridgeEventQueue()
    try:
        first.put_nowait("abcdef")
        second.put_nowait("éé")
        with pytest.raises(asyncio.QueueFull):
            second.put_nowait("x")
        assert first.get_nowait() == "abcdef"
        second.put_nowait("123456")
        assert second.queued_bytes == 10
    finally:
        first.close()
        second.close()


@pytest.mark.asyncio
@pytest.mark.parametrize("ending", ["cancel", "close", "fail", "finish"])
async def test_waiting_producer_counts_and_releases_its_payload(small_budget: None, ending: str) -> None:
    first = _HTTPBridgeEventQueue(max_events=1)
    second = _HTTPBridgeEventQueue()
    first.put_nowait("abcdef")
    producer = asyncio.create_task(first.put("1234"))
    try:
        await asyncio.sleep(0)
        assert not producer.done()
        with pytest.raises(asyncio.QueueFull):
            second.put_nowait("x")
        if ending == "cancel":
            producer.cancel()
            with pytest.raises(asyncio.CancelledError):
                await producer
        else:
            if ending == "fail":
                first.fail("terminal")
            else:
                getattr(first, ending)()
            # Capacity is reusable before the woken producer gets another turn.
            second.put_nowait("1234")
            with pytest.raises(asyncio.QueueShutDown):
                await producer
            assert first.queued_bytes == (0 if ending == "close" else 6)
            return
        second.put_nowait("1234")
    finally:
        first.close()
        second.close()
        if not producer.done():
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)


def test_oversized_first_event_cannot_escape_the_process_budget(small_budget: None) -> None:
    queue = _HTTPBridgeEventQueue(max_bytes=1)
    try:
        with pytest.raises(asyncio.QueueFull):
            queue.put_nowait("x" * 11)
        assert queue.empty()
        assert queue.queued_bytes == 0
        queue.put_nowait("x" * 10)
    finally:
        queue.close()


def test_rejected_nowait_put_does_not_leak_a_reservation(small_budget: None) -> None:
    full = _HTTPBridgeEventQueue(max_events=1)
    sibling = _HTTPBridgeEventQueue()
    try:
        full.put_nowait("abcd")
        for _ in range(3):
            with pytest.raises(asyncio.QueueFull):
                full.put_nowait("123456")
        sibling.put_nowait("123456")
    finally:
        full.close()
        sibling.close()


def test_abandoned_queue_releases_its_payload(small_budget: None) -> None:
    abandoned = _HTTPBridgeEventQueue()
    abandoned.put_nowait("0123456789")
    rejected = _HTTPBridgeEventQueue()
    try:
        with pytest.raises(asyncio.QueueFull):
            rejected.put_nowait("x")
    finally:
        rejected.close()
    del abandoned
    gc.collect()
    replacement = _HTTPBridgeEventQueue()
    try:
        replacement.put_nowait("0123456789")
    finally:
        replacement.close()


@pytest.mark.asyncio
async def test_async_put_reserves_once_then_releases_on_drain(small_budget: None) -> None:
    queue = _HTTPBridgeEventQueue(max_events=1)
    sibling = _HTTPBridgeEventQueue()
    try:
        await queue.put("0123456789")
        with pytest.raises(asyncio.QueueFull):
            sibling.put_nowait("x")
        assert await queue.get() == "0123456789"
        await sibling.put("0123456789")
    finally:
        queue.close()
        sibling.close()


@pytest.mark.asyncio
async def test_waiting_reservation_transfers_to_queued_ownership(small_budget: None) -> None:
    queue = _HTTPBridgeEventQueue(max_events=1)
    sibling = _HTTPBridgeEventQueue()
    queue.put_nowait("abcdef")
    producer = asyncio.create_task(queue.put("1234"))
    try:
        await asyncio.sleep(0)
        assert not producer.done()
        assert await queue.get() == "abcdef"
        await producer
        sibling.put_nowait("abcdef")
        with pytest.raises(asyncio.QueueFull):
            sibling.put_nowait("x")
        assert await queue.get() == "1234"
    finally:
        queue.close()
        sibling.close()
        if not producer.done():
            producer.cancel()
            await asyncio.gather(producer, return_exceptions=True)


@pytest.mark.asyncio
async def test_process_budget_failure_retains_prefix_then_terminal_and_sibling_progress(small_budget: None) -> None:
    queue = _HTTPBridgeEventQueue()
    sibling = _HTTPBridgeEventQueue()
    state = SimpleNamespace(request_id="request", response_id="response", bridge_request_deadline=None)
    settings = SimpleNamespace(stream_idle_timeout_seconds=7200)
    try:
        queue.put_nowait("prefix")
        assert not await _enqueue_http_bridge_downstream_event(queue, "exceeds", request_state=state, settings=settings)
        assert state.failure_phase_override == "downstream"
        assert state.failure_detail_override == "consumer_backpressure"
        assert await queue.get() == "prefix"
        terminal = await queue.get()
        assert terminal is not None and '"type":"response.failed"' in terminal
        assert await queue.get() is None
        assert await queue.get() is None
        assert queue.queued_bytes == 0
        assert await _enqueue_http_bridge_downstream_event(sibling, "0123456789", settings=settings)
        assert await sibling.get() == "0123456789"
    finally:
        queue.close()
        sibling.close()
