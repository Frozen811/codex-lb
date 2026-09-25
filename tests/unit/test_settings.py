from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.modules.settings.repository as settings_repo_module
from app.db.models import DashboardSettings
from app.modules.settings.repository import ModelContextWindowOverridesRepository, SettingsRepository


@pytest.mark.asyncio
async def test_commit_refresh_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    settings = DashboardSettings(id=1, version=1)

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(settings_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = SettingsRepository(session)
    await repo.commit_refresh(settings)
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_get_or_create_initial_seed_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(settings_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = SettingsRepository(session)
    res = await repo.get_or_create()
    assert res is not None
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_overrides_upsert_and_delete_use_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.get_bind.return_value.dialect.name = "sqlite"
    session.execute = AsyncMock()
    session.commit = AsyncMock()
    session.get = AsyncMock(return_value=MagicMock())
    session.delete = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(settings_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = ModelContextWindowOverridesRepository(session)
    await repo.upsert("gpt-4o", 128000)
    assert order == ["lock-enter", "lock-exit"]

    order.clear()
    await repo.delete("gpt-4o")
    assert order == ["lock-enter", "lock-exit"]
