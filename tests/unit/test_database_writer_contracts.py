from __future__ import annotations

import asyncio
import contextvars
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path
from types import SimpleNamespace

import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

import app.core.scheduling.leader_election as leader_module
import app.db.session as db
import app.modules.oauth.service as oauth_module
from app.core.config.key_fingerprint import verify_encryption_key_fingerprint
from app.core.rate_limiter.db_rate_limiter import DatabaseRateLimiter
from app.core.scheduling.leader_election import LeaderElection
from app.db.models import Base, OAuthFlowState, RateLimitAttempt, RuntimeSentinel
from app.modules.accounts.repository import AccountsRepository
from app.modules.oauth.repository import OAuthFlowRecord
from app.modules.oauth.service import OauthService

pytestmark = pytest.mark.unit


@pytest.fixture
async def writer_db(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    url = f"sqlite+aiosqlite:///{(tmp_path / 'writers.db').as_posix()}"
    engine = create_async_engine(url, poolclass=NullPool, connect_args={"timeout": 0.01})
    async with engine.begin() as connection:
        await connection.execute(text("PRAGMA journal_mode=WAL"))
        await connection.run_sync(
            lambda conn: Base.metadata.create_all(
                conn,
                tables=[
                    Base.metadata.tables["rate_limit_attempts"],
                    Base.metadata.tables["oauth_flow_states"],
                    Base.metadata.tables["runtime_sentinels"],
                    Base.metadata.tables["scheduler_leader"],
                ],
            )
        )
    monkeypatch.setattr(db, "_settings", SimpleNamespace(database_url=url))
    monkeypatch.setattr(db, "_sqlite_writer_lock", None)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    @asynccontextmanager
    async def background_session() -> AsyncIterator[AsyncSession]:
        async with factory() as session:
            yield session

    monkeypatch.setattr(oauth_module, "get_background_session", background_session)
    monkeypatch.setattr(leader_module, "get_background_session", background_session)
    monkeypatch.setattr(
        leader_module,
        "get_settings",
        lambda: SimpleNamespace(leader_election_enabled=True, leader_election_ttl_seconds=30),
    )
    try:
        yield factory
    finally:
        await engine.dispose()


async def test_writer_child_cannot_inherit_admission(writer_db: async_sessionmaker[AsyncSession]) -> None:
    attempted, entered = asyncio.Event(), asyncio.Event()

    async def child() -> None:
        attempted.set()
        async with db.sqlite_writer_section():
            entered.set()

    task: asyncio.Task[None] | None = None
    try:
        async with db.sqlite_writer_section():
            async with db.sqlite_writer_section():
                task = asyncio.create_task(child())
                await attempted.wait()
                with pytest.raises(TimeoutError):
                    await asyncio.wait_for(entered.wait(), 0.05)
        await asyncio.wait_for(task, 1)
        assert entered.is_set()
    finally:
        if task is not None:
            await asyncio.gather(task, return_exceptions=True)


async def test_cancelled_waiter_does_not_release_parent_admission(writer_db: async_sessionmaker[AsyncSession]) -> None:
    async def child() -> None:
        async with db.sqlite_writer_section():
            raise AssertionError("child entered its parent's write section")

    async with db.sqlite_writer_section():
        task = asyncio.create_task(child())
        await asyncio.sleep(0)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        async with db.sqlite_writer_section():
            pass
    async with db.sqlite_writer_section():
        pass


async def test_lease_recovers_after_cancelled_real_sqlite_writer(
    writer_db: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(db, "_background_session_factory", writer_db)
    writing = asyncio.Event()

    async def writer() -> None:
        async with db.sqlite_writer_section(), db.get_background_session() as session:
            await session.execute(
                text(
                    "INSERT INTO rate_limit_attempts (key, type, attempted_at) "
                    "VALUES ('cancelled', 'test', CURRENT_TIMESTAMP)"
                )
            )
            writing.set()
            await asyncio.Event().wait()

    task = asyncio.create_task(writer())
    await writing.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    election = LeaderElection("recovered-leader")
    assert await asyncio.wait_for(election.try_acquire(), 1)
    assert await election.renew()
    assert await election.release()
    async with writer_db() as session:
        assert not (await session.scalars(select(RateLimitAttempt))).all()


@pytest.mark.parametrize(
    "operation",
    [
        "admit",
        "failure",
        "clear",
        "sweep",
        "oauth",
        "oauth_status",
        "fingerprint",
        "acquire",
        "renew",
        "drain_renew",
        "release",
    ],
)
async def test_control_write_waits_for_real_sqlite_writer(
    writer_db: async_sessionmaker[AsyncSession], tmp_path: Path, operation: str
) -> None:
    election = LeaderElection("writer-test")
    if operation in {"renew", "drain_renew", "release"}:
        assert await election.try_acquire()
    if operation == "oauth_status":
        async with writer_db() as session:
            await OauthService(AccountsRepository(session))._persist_flow_record(
                OAuthFlowRecord(flow_id="test-flow", method="browser", status="pending")
            )

    async def control_write() -> None:
        async with writer_db() as session:
            limiter = DatabaseRateLimiter(8, 60, "password")
            if operation == "admit":
                await limiter.check_and_increment("client", session)
            elif operation == "failure":
                await limiter.record_failure("client", session)
            elif operation == "clear":
                await limiter.clear_for_key("client", session)
            elif operation == "sweep":
                await limiter.cleanup(session)
            elif operation == "oauth":
                await OauthService(AccountsRepository(session))._persist_flow_record(
                    OAuthFlowRecord(flow_id="test-flow", method="browser", status="pending")
                )
            elif operation == "oauth_status":
                assert await OauthService(AccountsRepository(session))._persist_flow_status(
                    "test-flow", status="success", error_message=None
                )
            elif operation == "fingerprint":
                await verify_encryption_key_fingerprint(writer_db, key_file=tmp_path / "key", mode="enforce")
            elif operation == "acquire":
                assert await election.try_acquire()
            elif operation == "renew":
                assert await election.renew()
            elif operation == "drain_renew":
                assert await election._renew_lease_row()
            else:
                assert await election.release()

    task: asyncio.Task[None] | None = None
    try:
        async with db.sqlite_writer_section():
            async with writer_db() as holder:
                await holder.execute(
                    text(
                        "INSERT INTO rate_limit_attempts (key, type, attempted_at) "
                        "VALUES ('holder', 'test', CURRENT_TIMESTAMP)"
                    )
                )
                task = asyncio.create_task(control_write(), context=contextvars.Context())
                await asyncio.sleep(0.6 if operation == "fingerprint" else 0.2)
                assert not task.done(), "control-plane write bypassed admission and exhausted SQLite's busy timeout"
                await holder.rollback()
        await asyncio.wait_for(task, 2)
        async with writer_db() as session:
            if operation in {"admit", "failure"}:
                assert len((await session.scalars(select(RateLimitAttempt))).all()) == 1
            elif operation in {"oauth", "oauth_status"}:
                flow = await session.get(OAuthFlowState, "test-flow")
                assert flow is not None and flow.status == ("success" if operation == "oauth_status" else "pending")
            elif operation == "fingerprint":
                assert await session.get(RuntimeSentinel, "encryption_key_fingerprint") is not None
    finally:
        if task is not None:
            await asyncio.gather(task, return_exceptions=True)


@pytest.mark.parametrize("cancel", [False, True])
async def test_reclaim_failure_or_cancellation_preserves_writer_recovery(
    writer_db: async_sessionmaker[AsyncSession], monkeypatch: pytest.MonkeyPatch, cancel: bool
) -> None:
    session = writer_db()
    await session.execute(
        text("INSERT INTO rate_limit_attempts (key, type, attempted_at) VALUES ('holder', 'test', CURRENT_TIMESTAMP)")
    )
    held = db._session_sync_connections(session)
    driver = held[0].connection.driver_connection
    interrupt_started, interrupt_release, teardown_release = asyncio.Event(), asyncio.Event(), asyncio.Event()

    async def interrupt() -> None:
        interrupt_started.set()
        if cancel:
            await interrupt_release.wait()
        else:
            raise sqlite3.ProgrammingError("Cannot operate on a closed database")

    monkeypatch.setattr(driver, "interrupt", interrupt)
    abandoned = asyncio.create_task(teardown_release.wait())
    reclaim = asyncio.create_task(
        db._reclaim_wedged_sqlite_session(session, abandoned, held, phase="rollback", elapsed_seconds=6)
    )
    try:
        await interrupt_started.wait()
        if cancel:
            reclaim.cancel()
            await asyncio.sleep(0)
            interrupt_release.set()
            with pytest.raises(asyncio.CancelledError):
                await reclaim
        else:
            await reclaim
        assert held[0].invalidated
        async with writer_db() as next_writer:
            await next_writer.execute(
                text(
                    "INSERT INTO rate_limit_attempts (key, type, attempted_at) "
                    "VALUES ('next', 'test', CURRENT_TIMESTAMP)"
                )
            )
            await next_writer.commit()
    finally:
        interrupt_release.set()
        teardown_release.set()
        await asyncio.gather(reclaim, abandoned, return_exceptions=True)
        for _ in range(10):
            pending = tuple(db._wedged_teardown_cleanup_tasks)
            if not pending:
                break
            await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), 2)
            await asyncio.sleep(0)
        await session.close()
    assert not db._wedged_teardown_cleanup_tasks
