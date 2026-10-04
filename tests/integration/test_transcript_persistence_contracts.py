from __future__ import annotations

import asyncio
from datetime import timedelta

import pytest
from sqlalchemy import update

from app.core.utils.time import utcnow
from app.db.models import HttpBridgeOperationRecord, HttpBridgeSessionRecord
from app.db.session import SessionLocal
from app.modules.proxy.durable_bridge_coordinator import DurableBridgeSessionCoordinator
from app.modules.proxy.http_bridge_event_batcher import HttpBridgeOperationEventBatcher

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("spool_format", ["rows_v1", "chunks_v2"])
async def test_transcript_backlog_real_persistence_order_terminal_and_owner_fence(db_setup, monkeypatch, spool_format):
    async with SessionLocal() as session:
        session.add(
            HttpBridgeSessionRecord(
                id="backlog-session",
                session_key_kind="session_header",
                session_key_value="backlog",
                session_key_hash="a" * 64,
                api_key_scope="scope",
                owner_instance_id="owner",
                owner_epoch=7,
                lease_expires_at=utcnow() + timedelta(minutes=5),
            )
        )
        await session.flush()
        session.add_all(
            [
                HttpBridgeOperationRecord(
                    operation_id=operation_id,
                    session_id="backlog-session",
                    request_fingerprint=operation_id.ljust(64, "a"),
                    state="submitted",
                    spool_format=spool_format,
                )
                for operation_id in ["good", "stale"]
            ]
        )
        await session.commit()
    coordinator = DurableBridgeSessionCoordinator(SessionLocal)
    method = "append_operation_events" if spool_format == "rows_v1" else "append_operation_event_chunk"
    original_append = getattr(coordinator, method)
    drained = asyncio.Event()
    calls = []

    async def tracked_append(**kwargs):
        persisted = await original_append(**kwargs)
        calls.append((len(kwargs["events"]), persisted))
        if len(calls) == 10:
            drained.set()
        return persisted

    monkeypatch.setattr(coordinator, method, tracked_append)
    batcher = HttpBridgeOperationEventBatcher(
        coordinator, max_bytes=2**20, batch_size=32, flush_interval_seconds=60, spool_format=spool_format
    )
    events = [f'data: {{"type":"response.output_text.delta","delta":"{i}"}}\n\n' for i in range(320)]
    terminal = 'data: {"type":"response.completed","response":{"id":"resp-backlog"}}\n\n'
    try:
        for event_text in events:
            await batcher.enqueue(
                operation_id="good",
                session_id="backlog-session",
                instance_id="owner",
                owner_epoch=7,
                event_text=event_text,
            )
        await asyncio.wait_for(drained.wait(), timeout=5)
        assert calls == [(32, True)] * 10
        result = await batcher.append_terminal_event(
            operation_id="good",
            session_id="backlog-session",
            instance_id="owner",
            owner_epoch=7,
            event_text=terminal,
            max_bytes=2**20,
            state="completed",
            response_id="resp-backlog",
        )
        assert result.persisted is True and result.settlement_required is False
        assert await coordinator.get_operation_events(operation_id="good") == [*events, terminal]
        snapshot = await coordinator.get_operation(operation_id="good")
        assert snapshot is not None and snapshot.state == "completed" and snapshot.event_spool_complete

        async with SessionLocal() as session:
            await session.execute(update(HttpBridgeSessionRecord).values(owner_epoch=8))
            await session.commit()
        await batcher.enqueue(
            operation_id="stale",
            session_id="backlog-session",
            instance_id="owner",
            owner_epoch=7,
            event_text="stale-event",
        )
        await batcher.flush_pending_operation(operation_id="stale")
        assert await coordinator.get_operation_events(operation_id="stale") == []
        snapshot = await coordinator.get_operation(operation_id="stale")
        assert snapshot is not None and snapshot.event_spool_complete is False
    finally:
        await batcher.close()
