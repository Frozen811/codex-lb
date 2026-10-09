from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.scheduling import task_shutdown
from app.modules.proxy import ring_membership
from app.modules.proxy._service.request_log import _RequestLogMixin

pytestmark = pytest.mark.unit


class PersistenceOwners(_RequestLogMixin):
    def __init__(self) -> None:
        self._request_log_tasks: set[asyncio.Task[None]] = set()
        self._background_cleanup_tasks: set[asyncio.Task[None]] = set()


@pytest.mark.asyncio
async def test_completed_settlement_stays_pending_before_ownership_callback() -> None:
    owners = PersistenceOwners()
    snapshots: list[dict[str, int | bool]] = []
    fallback_gate = asyncio.Event()

    async def settle() -> None:
        # Schedule the observer before the task's done callbacks, reproducing
        # status arriving after completion but before fallback ownership transfer.
        asyncio.get_running_loop().call_soon(
            lambda: snapshots.append(owners.request_persistence_activity_snapshot_nowait())
        )

    async def release_reservation() -> None:
        await fallback_gate.wait()

    def transfer_ownership(done: asyncio.Task[None]) -> None:
        owners._background_cleanup_tasks.discard(done)
        fallback = asyncio.create_task(release_reservation(), name="proxy-release_stream_api_key_reservation-req")
        owners._background_cleanup_tasks.add(fallback)
        fallback.add_done_callback(owners._background_cleanup_tasks.discard)

    task = asyncio.create_task(settle(), name="proxy-stream-api-key-settle-req")
    owners._background_cleanup_tasks.add(task)
    task.add_done_callback(transfer_ownership)
    try:
        await task
        assert snapshots[0]["request_persistence_pending"] == 1
        assert snapshots[0]["api_key_settlements_pending"] == 1
        assert owners.request_persistence_activity_snapshot_nowait()["request_persistence_pending"] == 1
    finally:
        fallback_gate.set()
        await asyncio.gather(*owners._background_cleanup_tasks)
        await asyncio.sleep(0)
    assert owners.request_persistence_activity_snapshot_nowait()["request_persistence_pending"] == 0


@pytest.mark.asyncio
async def test_interrupted_fallback_stop_retains_database_cleanup_owner(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(task_shutdown, "DATABASE_TASK_STOP_GRACE_SECONDS", 0.01)
    cleanup_started = asyncio.Event()
    cleanup_release = asyncio.Event()

    async def database_work() -> None:
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            cleanup_started.set()
            await cleanup_release.wait()
            raise

    worker = asyncio.create_task(database_work())
    stopper = asyncio.create_task(task_shutdown.stop_task_after_grace(worker))
    try:
        await asyncio.wait_for(cleanup_started.wait(), timeout=1)
        stopper.cancel()
        with pytest.raises(asyncio.CancelledError):
            await stopper
        assert not worker.done()
        assert worker in task_shutdown.undrained_tasks()
    finally:
        cleanup_release.set()
        await asyncio.gather(worker, stopper, return_exceptions=True)
    assert worker not in task_shutdown.undrained_tasks()


@pytest.mark.asyncio
async def test_ring_heartbeat_uses_background_provider_by_default(monkeypatch: pytest.MonkeyPatch) -> None:
    entered = asyncio.Event()
    exited = asyncio.Event()
    session = AsyncMock()
    session.get_bind = lambda: SimpleNamespace(dialect=SimpleNamespace(name="sqlite"))

    @asynccontextmanager
    async def background_session():
        entered.set()
        try:
            yield session
        finally:
            exited.set()

    monkeypatch.setattr(ring_membership, "get_background_session", background_session)
    await ring_membership.RingMembershipService().heartbeat("instance-background")
    assert entered.is_set() and exited.is_set()
    session.execute.assert_awaited_once()
    session.commit.assert_awaited_once()
