from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace

import pytest
from sqlalchemy import delete, select, update

from app.core.utils.sse import parse_sse_data_json
from app.db.models import HttpBridgeRetryCircuit
from app.db.session import SessionLocal
from app.modules.proxy._service.http_bridge import upstream_events
from app.modules.proxy._service.http_bridge.queues import _HTTPBridgeEventQueue
from app.modules.proxy._service.http_bridge.upstream_events import _enqueue_http_bridge_downstream_event
from app.modules.proxy.downstream_delivery import DeliveryTracedStreamingResponse
from app.modules.proxy.durable_bridge_repository import DurableBridgeRepository, durable_bridge_hash
from app.modules.sticky_sessions import cleanup_scheduler

pytestmark = pytest.mark.unit


@pytest.fixture
def async_session_factory(db_setup):
    return SessionLocal


@pytest.mark.asyncio
@pytest.mark.parametrize("race", ["count", "generation", "epoch"])
@pytest.mark.parametrize("mixed_batch", [False, True])
@pytest.mark.parametrize("batch_size", [1, 128])
async def test_scheduled_cleanup_preserves_changed_candidate_for_whole_pass(
    async_session_factory, monkeypatch, race, mixed_batch, batch_size
):
    target_hash = durable_bridge_hash("cleanup-race")
    async with async_session_factory() as database:
        database.add(
            HttpBridgeRetryCircuit(
                session_key_kind="session_header",
                session_key_hash=target_hash,
                api_key_scope="scope",
                consecutive_failures=2,
                cooldown_until_epoch=0,
                admission_generation=0,
                updated_at_epoch=1,
                last_detail="stream_incomplete",
            )
        )
        if mixed_batch:
            database.add(
                HttpBridgeRetryCircuit(
                    session_key_kind="session_header",
                    session_key_hash="f" * 64,
                    api_key_scope="scope",
                    consecutive_failures=2,
                    cooldown_until_epoch=0,
                    admission_generation=0,
                    updated_at_epoch=1,
                    last_detail="stream_incomplete",
                )
            )
        await database.commit()

    changed = False
    original_purge = DurableBridgeRepository.purge_retry_circuits_before

    async def instrumented_purge(repository, *args, **kwargs):
        original_execute = repository._session.execute

        async def execute(statement, *execute_args, **execute_kwargs):
            nonlocal changed
            if isinstance(statement, type(delete(HttpBridgeRetryCircuit))) and not changed:
                changed = True
                values = {
                    "count": {"consecutive_failures": 3},
                    "generation": {"admission_generation": 1},
                    "epoch": {"updated_at_epoch": 2},
                }[race]
                await original_execute(
                    update(HttpBridgeRetryCircuit)
                    .where(HttpBridgeRetryCircuit.session_key_hash == target_hash)
                    .values(**values)
                )
            return await original_execute(statement, *execute_args, **execute_kwargs)

        monkeypatch.setattr(repository._session, "execute", execute)
        return await original_purge(repository, *args, **kwargs, batch_size=batch_size)

    monkeypatch.setattr(DurableBridgeRepository, "purge_retry_circuits_before", instrumented_purge)

    @asynccontextmanager
    async def background_session():
        async with async_session_factory() as database:
            yield database

    monkeypatch.setattr(cleanup_scheduler, "get_background_session", background_session)
    scheduler = cleanup_scheduler.StickySessionCleanupScheduler(
        interval_seconds=60, enabled=True, operation_retention_enabled=False
    )
    await scheduler._cleanup_as_leader()
    assert changed, "the real scheduled pass must reach candidate deletion"
    async with async_session_factory() as database:
        rows = list(await database.scalars(select(HttpBridgeRetryCircuit)))
    assert len(rows) == 1
    assert rows[0].session_key_hash == target_hash
    assert rows[0].consecutive_failures == (3 if race == "count" else 2)
    assert rows[0].admission_generation == (1 if race == "generation" else 0)
    assert rows[0].updated_at_epoch == (2 if race == "epoch" else 1)


@pytest.mark.asyncio
async def test_closed_queue_releases_buffer_and_cancelled_producer_waiters():
    queue = _HTTPBridgeEventQueue(max_events=1, max_bytes=10)
    queue.put_nowait("1234567890")
    producer = asyncio.create_task(queue.put("blocked"))
    await asyncio.sleep(0)
    assert len(queue._putters) == 1
    producer.cancel()
    with pytest.raises(asyncio.CancelledError):
        await producer
    assert not queue._putters
    queue.close()
    assert queue.queued_bytes == 0
    assert queue.qsize() == 0


@pytest.mark.asyncio
async def test_delivery_stall_retains_order_then_reports_failure():
    queue = _HTTPBridgeEventQueue(max_events=1, max_bytes=10)
    queue.put_nowait("old-output")
    request = SimpleNamespace(
        request_id="stalled", response_id="resp-stalled", draining_until_terminal=False, bridge_request_deadline=None
    )
    settings = SimpleNamespace(stream_idle_timeout_seconds=0.01)
    assert not await _enqueue_http_bridge_downstream_event(
        queue, "lost-output", request_state=request, settings=settings
    )
    assert await queue.get() == "old-output"
    terminal_text = await asyncio.wait_for(queue.get(), timeout=0.1)
    assert terminal_text is not None
    terminal = parse_sse_data_json(terminal_text)
    assert terminal is not None
    assert terminal["type"] == "response.failed"
    response = terminal["response"]
    assert isinstance(response, dict)
    error = response["error"]
    assert isinstance(error, dict)
    assert error["code"] == "stream_idle_timeout"
    assert await asyncio.wait_for(queue.get(), timeout=0.1) is None
    assert queue.queued_bytes == 0
    assert not queue._putters


@pytest.mark.asyncio
async def test_closed_terminal_queue_does_not_cancel_the_reader():
    queue = _HTTPBridgeEventQueue(max_events=1, max_bytes=10)
    queue.close()
    request = SimpleNamespace(request_id="detached", draining_until_terminal=True)
    await _enqueue_http_bridge_downstream_event(queue, None, request_state=request)
    assert await queue.get() is None


@pytest.mark.asyncio
async def test_terminal_sentinel_does_not_stall_or_replace_accepted_success():
    queue = _HTTPBridgeEventQueue(max_events=1, max_bytes=10)
    queue.put_nowait("completed")
    assert await _enqueue_http_bridge_downstream_event(queue, None)
    assert await queue.get() == "completed"
    assert await queue.get() is None


@pytest.mark.asyncio
async def test_long_model_idle_allowance_does_not_extend_downstream_stall(monkeypatch):
    # Shorten only the fixed delivery bound, retaining the real two-hour model
    # idle allowance. A timed wait must choose the delivery bound.
    monkeypatch.setattr(upstream_events, "_HTTP_BRIDGE_DOWNSTREAM_STALL_TIMEOUT_SECONDS", 0.01)
    queue = _HTTPBridgeEventQueue(max_events=1, max_bytes=10)
    queue.put_nowait("output")
    request = SimpleNamespace(request_id="bounded", response_id=None, bridge_request_deadline=None)
    assert not await asyncio.wait_for(
        _enqueue_http_bridge_downstream_event(
            queue, "blocked", request_state=request, settings=SimpleNamespace(stream_idle_timeout_seconds=7200)
        ),
        timeout=0.1,
    )
    assert await queue.get() == "output"
    terminal_text = await queue.get()
    assert terminal_text is not None
    terminal = parse_sse_data_json(terminal_text)
    assert terminal is not None and terminal["type"] == "response.failed"


@pytest.mark.asyncio
async def test_response_send_repeated_cancellation_awaits_iterator_cleanup():
    sending = asyncio.Event()
    closing = asyncio.Event()
    release_cleanup = asyncio.Event()
    closed = asyncio.Event()

    async def stream():
        try:
            yield 'event: response.created\ndata: {"type":"response.created"}\n\n'
        finally:
            closing.set()
            await release_cleanup.wait()
            closed.set()

    async def send(message):
        if message["type"] == "http.response.body":
            sending.set()
            await asyncio.Event().wait()

    async def receive():
        await asyncio.Event().wait()

    response = DeliveryTracedStreamingResponse(stream(), surface="responses")
    task = asyncio.create_task(
        response({"type": "http", "asgi": {"version": "3.0", "spec_version": "2.4"}}, receive, send)
    )
    try:
        await asyncio.wait_for(sending.wait(), timeout=1)
        task.cancel()
        await asyncio.wait_for(closing.wait(), timeout=1)
        task.cancel()
        await asyncio.sleep(0)
        assert not task.done()
        release_cleanup.set()
        with pytest.raises(asyncio.CancelledError):
            await asyncio.wait_for(task, timeout=1)
        assert closed.is_set()
        assert response.outcome == "cancelled_before_terminal"
    finally:
        release_cleanup.set()
        if not task.done():
            task.cancel()
            with pytest.raises(asyncio.CancelledError):
                await task
