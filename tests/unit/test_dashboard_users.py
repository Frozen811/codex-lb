from __future__ import annotations

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.modules.dashboard_users.repository as users_repo_module
from app.db.models import DashboardUser
from app.modules.dashboard_users.repository import DashboardUsersRepository


@pytest.mark.asyncio
async def test_commit_user_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.expire_all = MagicMock()
    user = DashboardUser(id="u1", username="admin")

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(users_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardUsersRepository(session)
    monkeypatch.setattr(repo, "get_by_id", AsyncMock(return_value=user))
    res = await repo.commit_user("u1")
    assert res == user
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_purge_expired_invited_users_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    scalars_mock = MagicMock()
    scalars_mock.all.return_value = ["u_expired"]
    res_mock = MagicMock()
    res_mock.scalars.return_value = scalars_mock
    session.execute = AsyncMock(return_value=res_mock)
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(users_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardUsersRepository(session)
    purged = await repo.purge_expired_invited_users(datetime.now(timezone.utc))
    assert purged == 1
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_reactivate_owner_disabled_keys_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    res_mock = MagicMock()
    res_mock.scalars.return_value.all.return_value = ["hash1"]
    session.execute = AsyncMock(return_value=res_mock)
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(users_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardUsersRepository(session)
    hashes = await repo.reactivate_owner_disabled_keys("u1")
    assert hashes == ["hash1"]
    assert order == ["lock-enter", "lock-exit"]




@pytest.mark.asyncio
async def test_delete_user_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    del_mock = MagicMock()
    del_mock.scalar_one_or_none.return_value = "u1"
    session.execute = AsyncMock(return_value=del_mock)
    session.commit = AsyncMock()
    user = DashboardUser(id="u1", username="test")

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(users_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardUsersRepository(session)
    monkeypatch.setattr(repo, "deactivate_owned_keys", AsyncMock(return_value=["k1"]))
    res = await repo.delete_user(user)
    assert res == ["k1"]
    assert "lock-enter" in order and "lock-exit" in order


@pytest.mark.asyncio
async def test_purge_expired_invited_users_skips_when_no_candidates(monkeypatch) -> None:
    session = MagicMock()
    first_res = MagicMock()
    first_res.first.return_value = None
    session.execute = AsyncMock(return_value=first_res)
    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(users_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardUsersRepository(session)
    purged = await repo.purge_expired_invited_users(datetime.now(timezone.utc))
    assert purged == 0
    assert order == []


@pytest.mark.asyncio
async def test_acquire_write_intent_executes_begin_immediate_on_sqlite() -> None:
    session = MagicMock()
    session.get_bind.return_value.dialect.name = "sqlite"
    session.execute = AsyncMock()

    repo = DashboardUsersRepository(session)
    await repo.acquire_write_intent()
    session.execute.assert_awaited_once()
    assert "BEGIN IMMEDIATE" in str(session.execute.call_args[0][0])

