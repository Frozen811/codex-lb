from __future__ import annotations

import asyncio
from unittest.mock import Mock

import pytest

from app.modules.proxy._service.http_bridge.queues import (
    _HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT,
    _HTTP_BRIDGE_STREAM_QUEUE_LIMIT,
    _http_bridge_event_payload_size,
    _HTTPBridgeEventQueue,
    _new_http_bridge_event_queue,
)
from app.modules.proxy._service.http_bridge.upstream_events import (
    _enqueue_http_bridge_downstream_event,
)

pytestmark = pytest.mark.unit


def test_event_payload_size_measures_utf8_bytes() -> None:
    assert _http_bridge_event_payload_size(None) == 0
    assert _http_bridge_event_payload_size("") == 0
    assert _http_bridge_event_payload_size("hello") == 5
    assert _http_bridge_event_payload_size("é") == 2
    assert _http_bridge_event_payload_size(123) == 0


def test_http_bridge_event_queue_defaults() -> None:
    queue = _new_http_bridge_event_queue()
    assert queue.maxsize == _HTTP_BRIDGE_STREAM_QUEUE_LIMIT
    assert queue._max_bytes == _HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT
    assert queue.queued_bytes == 0


def test_http_bridge_event_queue_trips_on_bytes_or_events_and_releases_bytes_on_get() -> None:
    queue = _HTTPBridgeEventQueue(max_events=4, max_bytes=10)
    queue.put_nowait("abcd")  # 4 bytes
    queue.put_nowait("efgh")  # 4 bytes (total 8)
    assert queue.queued_bytes == 8 and not queue.full()

    # An event that would exceed the 10-byte budget is rejected by put_nowait
    with pytest.raises(asyncio.QueueFull):
        queue.put_nowait("klm")  # 8 + 3 > 10

    # Exactly 2 bytes fills the budget to 10
    queue.put_nowait("ij")
    assert queue.queued_bytes == 10

    # A zero-byte terminal at exactly the budget is still accepted (event cap has room)
    queue.put_nowait(None)
    assert queue.full()  # 4 items is the max_events cap

    with pytest.raises(asyncio.QueueFull):
        queue.put_nowait(None)

    # get_nowait releases bytes
    assert queue.get_nowait() == "abcd"
    assert queue.queued_bytes == 6 and not queue.full()

    with pytest.raises(asyncio.QueueFull):
        queue.put_nowait("12345")  # 6 + 5 > 10

    queue.put_nowait("1234")  # 6 + 4 == 10
    assert queue.queued_bytes == 10


def test_http_bridge_event_queue_accepts_lone_chunk_larger_than_budget() -> None:
    queue = _HTTPBridgeEventQueue(max_events=8, max_bytes=10)
    # A single event larger than the whole budget is accepted at an empty queue
    queue.put_nowait("x" * 64)
    assert queue.queued_bytes == 64

    # Subsequent non-empty event is rejected
    with pytest.raises(asyncio.QueueFull):
        queue.put_nowait("y")

    # Zero-byte terminal still accepted
    queue.put_nowait(None)
    assert queue.get_nowait() == "x" * 64
    assert queue.get_nowait() is None
    assert queue.queued_bytes == 0


@pytest.mark.asyncio
async def test_http_bridge_event_queue_put_waits_for_space_and_wakes_on_get() -> None:
    queue = _HTTPBridgeEventQueue(max_events=4, max_bytes=10)
    queue.put_nowait("12345678")  # 8 bytes

    put_finished = False

    async def put_item() -> None:
        nonlocal put_finished
        await queue.put("1234")  # 8 + 4 > 10, must wait
        put_finished = True

    put_task = asyncio.create_task(put_item())
    await asyncio.sleep(0.01)
    assert not put_finished

    # Drain item to free bytes
    assert await queue.get() == "12345678"
    await asyncio.sleep(0.01)
    assert put_finished
    await put_task
    assert queue.queued_bytes == 4


@pytest.mark.asyncio
async def test_http_bridge_event_queue_close_cancels_waiters() -> None:
    queue = _HTTPBridgeEventQueue(max_events=2, max_bytes=10)
    queue.put_nowait("1234567890")  # exactly full

    async def blocked_put() -> None:
        await queue.put("more")

    put_task = asyncio.create_task(blocked_put())
    await asyncio.sleep(0.01)
    assert not put_task.done()

    queue.close()
    await asyncio.sleep(0.01)
    assert put_task.done()
    with pytest.raises(asyncio.CancelledError):
        await put_task


@pytest.mark.asyncio
async def test_enqueue_http_bridge_downstream_event_handles_detach_and_timeout() -> None:
    queue = _HTTPBridgeEventQueue(max_events=2, max_bytes=10)
    queue.put_nowait("1234567890")  # full

    request_state = Mock()
    request_state.request_id = "req-1"
    request_state.draining_until_terminal = True
    request_state.bridge_request_deadline = None

    # When request is already detached and closed, it returns False without raising
    queue.close()
    result = await _enqueue_http_bridge_downstream_event(
        queue,
        "new_event",
        request_state=request_state,
    )
    assert result is False

    # When stalled beyond timeout
    stalled_queue = _HTTPBridgeEventQueue(max_events=1, max_bytes=5)
    stalled_queue.put_nowait("12345")
    stalled_request = Mock()
    stalled_request.request_id = "req-stalled"
    stalled_request.draining_until_terminal = False
    stalled_request.bridge_request_deadline = 0.05  # will timeout immediately

    clock = Mock()
    clock.monotonic.return_value = 1.0  # past deadline

    result = await _enqueue_http_bridge_downstream_event(
        stalled_queue,
        "stall_event",
        request_state=stalled_request,
        clock=clock,
    )
    assert result is False
    assert stalled_request.failure_phase_override == "downstream"
    assert stalled_request.failure_detail_override == "consumer_backpressure"
