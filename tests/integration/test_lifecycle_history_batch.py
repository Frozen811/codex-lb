from __future__ import annotations

import asyncio
from importlib import import_module
from types import SimpleNamespace
from typing import cast
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Table
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.testclient import TestClient, WebSocketDenialResponse

from app.core import shutdown as shutdown_state
from app.core.cache.invalidation import CacheInvalidationPoller
from app.db import session as db_session
from app.db.models import CacheInvalidation
from app.dependencies import get_proxy_service_for_app
from app.main import create_app
from app.modules.proxy.ring_membership import RingMembershipService
from app.modules.proxy.service import ProxyService

pytestmark = pytest.mark.integration
app_main = import_module("app.main")


def _activity(count: int = 0) -> dict[str, int | bool]:
    return {
        "request_persistence_pending": count,
        "request_persistence_active": count > 0,
        "api_key_settlements_pending": count,
        "persistence_drain_active": count > 0,
    }


@pytest.mark.asyncio
async def test_poller_finishes_held_sqlite_read_before_stop_returns(tmp_path, monkeypatch) -> None:
    engine = create_async_engine(f"sqlite+aiosqlite:///{tmp_path / 'owned-read.db'}")
    async with engine.begin() as connection:
        await connection.run_sync(
            lambda sync: CacheInvalidation.metadata.create_all(sync, tables=[cast(Table, CacheInvalidation.__table__)])
        )
    session = async_sessionmaker(engine)()
    real_execute = session.execute
    read_open = asyncio.Event()
    release = asyncio.Event()
    read_completed = asyncio.Event()

    async def held_execute(*args, **kwargs):
        result = await real_execute(*args, **kwargs)
        read_open.set()
        await release.wait()
        read_completed.set()
        return result

    monkeypatch.setattr(session, "execute", held_execute)
    poller = CacheInvalidationPoller(lambda: session)
    stopper = None
    try:
        await poller.start()
        await asyncio.wait_for(read_open.wait(), timeout=1)
        stopper = asyncio.create_task(poller.stop())
        await asyncio.wait_for(poller._stop.wait(), timeout=1)
        release.set()
        await stopper
        assert read_completed.is_set()
        assert not session.in_transaction()
    finally:
        release.set()
        if stopper is not None:
            await stopper
        await poller.stop()
        await session.close()
        await engine.dispose()


@pytest.mark.asyncio
async def test_lifespan_withholds_clean_shutdown_while_maintenance_cleanup_is_owned(db_setup, monkeypatch) -> None:
    from app.core.scheduling import task_shutdown

    entered = asyncio.Event()
    release = asyncio.Event()
    clean_checks: list[bool] = []
    close_db_and_record = app_main._close_db_and_record_clean_shutdown

    async def blocked_reconciliation(_self) -> None:
        entered.set()
        try:
            await asyncio.Event().wait()
        except asyncio.CancelledError:
            await release.wait()
            raise

    async def observe_clean_gate(**kwargs) -> None:
        clean_checks.append(kwargs["database_tasks_drained"])
        await close_db_and_record(**kwargs)

    monkeypatch.setattr(task_shutdown, "DATABASE_TASK_STOP_GRACE_SECONDS", 0.01)
    monkeypatch.setattr(app_main, "RING_HEARTBEAT_INTERVAL_SECONDS", 0.01)
    monkeypatch.setattr(app_main, "_close_db_and_record_clean_shutdown", observe_clean_gate)
    monkeypatch.setattr(ProxyService, "reconcile_durable_http_bridge_ownership", blocked_reconciliation)
    app = create_app()
    get_proxy_service_for_app(app)
    try:
        async with app.router.lifespan_context(app):
            await asyncio.wait_for(entered.wait(), timeout=2)
        assert clean_checks == [False]
        assert any(
            task.get_name() == "bridge-ring-maintenance-durable-ownership" for task in task_shutdown.undrained_tasks()
        )
    finally:
        release.set()
        await asyncio.gather(*task_shutdown.undrained_tasks(), return_exceptions=True)
        # Simulate process exit for this intentionally unclean test lifespan.
        # Release its file lock without stamping a false CLEAN record.
        db_session._release_sqlite_lifetime_lock()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "observation",
    [
        None,
        {},
        {**_activity(), "request_persistence_pending": True},
        {**_activity(), "request_persistence_pending": -1},
        {**_activity(), "request_persistence_pending": 1.5},
        {**_activity(), "request_persistence_pending": "0"},
        {**_activity(), "request_persistence_active": "false"},
        {**_activity(), "api_key_settlements_pending": 1},
        {**_activity(1), "persistence_drain_active": False},
        {**_activity(), "api_key_settlements_pending": True},
        "bad",
        RuntimeError("observer unavailable"),
    ],
)
async def test_internal_status_reports_unknown_for_invalid_observation(db_setup, observation) -> None:
    app = create_app()
    if observation is not None:
        observer = (
            MagicMock(side_effect=observation)
            if isinstance(observation, Exception)
            else MagicMock(return_value=observation)
        )
        app.state.proxy_service = SimpleNamespace(request_persistence_activity_snapshot_nowait=observer)
    shutdown_state.reset()
    async with AsyncClient(
        transport=ASGITransport(app=app, client=("127.0.0.1", 12345)), base_url="http://127.0.0.1"
    ) as client:
        response = await client.get("/internal/drain/status")
    assert response.status_code == 200
    checks = response.json()["checks"]
    assert checks["request_persistence_state"] == "unknown"
    assert "request_persistence_pending" not in checks


@pytest.mark.asyncio
async def test_internal_status_observes_real_detached_owners_and_completion(db_setup) -> None:
    app = create_app()
    service = get_proxy_service_for_app(app)
    release = asyncio.Event()

    async def owned_settlement() -> None:
        await release.wait()

    owner = asyncio.create_task(owned_settlement(), name="proxy-stream-api-key-settle-status")
    service._background_cleanup_tasks.add(owner)
    owner.add_done_callback(service._background_cleanup_tasks.discard)
    shutdown_state.reset()
    shutdown_state.begin_drain(30)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app, client=("127.0.0.1", 12345)), base_url="http://127.0.0.1"
        ) as client:
            pending = await client.get("/internal/drain/status")
            assert pending.status_code == 200
            checks = pending.json()["checks"]
            assert checks["in_flight"] == "0"
            assert checks["request_persistence_state"] == "pending"
            assert checks["request_persistence_pending"] == "1"
            assert checks["api_key_settlements_pending"] == "1"
            release.set()
            await owner
            drained = await client.get("/internal/drain/status")
            assert drained.json()["checks"]["request_persistence_state"] == "drained"
            assert drained.json()["checks"]["request_persistence_pending"] == "0"
    finally:
        release.set()
        await owner
        shutdown_state.reset()


@pytest.mark.parametrize(
    "path",
    [
        "/v1/responses",
        "/v1/responses/",
        "/backend-api/codex/responses",
        "/backend-api/codex/responses/",
        "/codex/responses",
        "/codex/responses/",
        "/ws/events",
        "/codex/responses-extra",
    ],
)
def test_draining_websocket_upgrade_has_retryable_http_denial(db_setup, path) -> None:
    app = create_app()
    shutdown_state.reset()
    shutdown_state.begin_drain(30)
    try:
        client = TestClient(app, client=("127.0.0.1", 12345))
        try:
            with pytest.raises(WebSocketDenialResponse) as denied:
                with client.websocket_connect(path):
                    pass
        finally:
            client.close()
        assert denied.value.status_code == 503
        assert denied.value.headers["retry-after"] == "5"
        if path in {"/ws/events", "/codex/responses-extra"}:
            assert denied.value.json() == {"detail": "Server is draining"}
        else:
            assert denied.value.json()["error"]["code"] == "proxy_unavailable"
            assert denied.value.json()["error"]["type"] == "server_error"
        assert shutdown_state.get_in_flight() == 0
    finally:
        shutdown_state.reset()


@pytest.mark.asyncio
async def test_lifespan_heartbeat_survives_blocked_optional_maintenance(db_setup, monkeypatch) -> None:
    maintenance_started = asyncio.Event()
    release = asyncio.Event()
    heartbeat_twice = asyncio.Event()
    counts = {"heartbeat": 0, "reconcile": 0, "sweep": 0, "abandon": 0, "caps": 0}

    async def reconcile(_self) -> None:
        counts["reconcile"] += 1
        maintenance_started.set()
        await release.wait()

    async def sweep(_self) -> None:
        counts["sweep"] += 1

    async def abandon(_self) -> None:
        counts["abandon"] += 1
        if counts["abandon"] == 1:
            raise RuntimeError("first stale-operation pass fails")

    async def caps(*_args) -> None:
        counts["caps"] += 1

    class ObservedRing(RingMembershipService):
        async def heartbeat(self, *args, **kwargs) -> None:
            await super().heartbeat(*args, **kwargs)
            counts["heartbeat"] += 1
            if counts["heartbeat"] >= 3:
                heartbeat_twice.set()

    monkeypatch.setattr(app_main, "RingMembershipService", ObservedRing)
    monkeypatch.setattr(app_main, "RING_HEARTBEAT_INTERVAL_SECONDS", 0.01)
    monkeypatch.setattr(app_main, "refresh_cap_partition", caps)
    monkeypatch.setattr(ProxyService, "reconcile_durable_http_bridge_ownership", reconcile)
    monkeypatch.setattr(ProxyService, "prune_idle_http_bridge_sessions", sweep)
    monkeypatch.setattr(ProxyService, "abandon_stale_http_bridge_operations", abandon)
    app = create_app()
    get_proxy_service_for_app(app)
    try:
        async with app.router.lifespan_context(app):
            await asyncio.wait_for(maintenance_started.wait(), timeout=2)
            try:
                await asyncio.wait_for(heartbeat_twice.wait(), timeout=0.5)
                assert counts["reconcile"] == 1
                assert counts["sweep"] >= 2
                assert counts["abandon"] >= 2
                assert counts["caps"] >= 2
            finally:
                release.set()
    finally:
        release.set()
