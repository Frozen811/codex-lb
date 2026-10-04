from __future__ import annotations

import asyncio
from collections import defaultdict
from time import perf_counter

import pytest

from app.modules.proxy.http_bridge_event_batcher import HttpBridgeOperationEventBatcher

pytestmark = pytest.mark.unit


class _CountingWake:
    def __init__(self):
        self.event = asyncio.Event()
        self.wait_count = 0

    async def wait(self):
        self.wait_count += 1
        await self.event.wait()

    def set(self):
        self.event.set()

    def clear(self):
        self.event.clear()


@pytest.mark.parametrize("failure", [None, "false", "exception"])
async def test_transcript_backlog_has_fair_passes_without_interval_waits(failure):
    wake = _CountingWake()
    drained = asyncio.Event()
    batches = []
    output = defaultdict(list)
    observed_waits = []

    class Writer:
        async def append_operation_events(self, *, events, max_bytes):
            operation_id = events[0].operation_id
            batches.append((operation_id, len(events)))
            observed_waits.append(wake.wait_count)
            await asyncio.sleep(0.001)
            if operation_id == "failed":
                if failure == "exception":
                    raise RuntimeError("optional persistence unavailable")
                return False
            output[operation_id].extend(event.event_text for event in events)
            if sum(map(len, output.values())) == 416:
                drained.set()
            return True

    batcher = HttpBridgeOperationEventBatcher(Writer(), max_bytes=2**20, batch_size=32, flush_interval_seconds=60)
    batcher._wake = wake
    try:
        for operation_id, count in [("failed", 64 if failure else 0), ("a", 320), ("b", 64), ("c", 32)]:
            for i in range(count):
                await batcher.enqueue(
                    operation_id=operation_id,
                    session_id="session",
                    instance_id="owner",
                    owner_epoch=1,
                    event_text=f"{operation_id}:{i}" + "x" * 1024,
                )
        started = perf_counter()
        await asyncio.wait_for(drained.wait(), timeout=3)
        elapsed = perf_counter() - started
        assert observed_waits == [1] * len(batches)
        successful_batches = [operation_id for operation_id, _ in batches if operation_id != "failed"]
        assert successful_batches[:5] == ["a", "b", "c", "a", "b"]
        assert successful_batches.count("a") == 10
        assert successful_batches.count("b") == 2
        assert successful_batches.count("c") == 1
        assert all(count == 32 for _, count in batches)
        for operation_id, count in [("a", 320), ("b", 64), ("c", 32)]:
            assert output[operation_id] == [f"{operation_id}:{i}" + "x" * 1024 for i in range(count)]
        if failure:
            assert "failed" in batcher._dropped_operations
            assert [operation_id for operation_id, _ in batches].count("failed") == 1
        assert batcher._pending_count == batcher._pending_bytes == 0
        print(f"transcript writes={len(batches)} initial-waits=1 drain={elapsed:.3f}s failure={failure}")
    finally:
        task = batcher._task
        await batcher.close()
        assert task is not None and task.done()
