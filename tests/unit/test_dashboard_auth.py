from __future__ import annotations

from contextlib import asynccontextmanager
from unittest.mock import AsyncMock, MagicMock

import pytest

import app.modules.dashboard_auth.oidc_flows as oidc_flows_module
import app.modules.dashboard_auth.repository as auth_repo_module
from app.db.models import DashboardSettings, DashboardUser
from app.modules.dashboard_auth.oidc_flows import OidcFlowPurpose, OidcFlowRepository
from app.modules.dashboard_auth.repository import DashboardAuthRepository


@pytest.mark.asyncio
async def test_store_bootstrap_token_if_absent_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = 1
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()
    session.get = AsyncMock(return_value=DashboardSettings(id=1))

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(auth_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardAuthRepository(session)
    res = await repo.store_bootstrap_token_if_absent(b"enc", b"hash")
    assert res is True
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_clear_bootstrap_token_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = 1
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()
    session.get = AsyncMock(return_value=DashboardSettings(id=1))

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(auth_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardAuthRepository(session)
    res = await repo.clear_bootstrap_token()
    assert res is True
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_write_user_apply_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()

    user = DashboardUser(id="user1", username="test", session_generation=1)

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(auth_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardAuthRepository(session)
    monkeypatch.setattr(repo, "_load_user", AsyncMock(return_value=user))

    def mutate(u: DashboardUser) -> None:
        u.username = "new_test"

    await repo._write_user("user1", mutate)
    assert order == ["lock-enter", "lock-exit"]
    assert session.commit.called


@pytest.mark.asyncio
async def test_try_advance_user_totp_step_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.scalar_one_or_none.return_value = "user1"
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(auth_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardAuthRepository(session)
    res = await repo.try_advance_user_totp_step("user1", 10)
    assert res is True
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_touch_last_login_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(auth_repo_module, "sqlite_writer_section", fake_writer_section)
    repo = DashboardAuthRepository(session)
    await repo.touch_last_login("user1")
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_oidc_flow_create_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.add = MagicMock()
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(oidc_flows_module, "sqlite_writer_section", fake_writer_section)
    repo = OidcFlowRepository(session)
    await repo.create(
        state_hash="state",
        provider_id="google",
        nonce_hash="nonce",
        code_verifier="verifier",
        purpose=OidcFlowPurpose.LOGIN,
        redirect_uri="http://callback",
        config_fingerprint="fp",
    )
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_oidc_flow_consume_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    result_mock = MagicMock()
    result_mock.first.return_value = None
    session.execute = AsyncMock(return_value=result_mock)
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(oidc_flows_module, "sqlite_writer_section", fake_writer_section)
    repo = OidcFlowRepository(session)
    await repo.consume("state")
    assert order == ["lock-enter", "lock-exit"]


@pytest.mark.asyncio
async def test_oidc_flow_purge_expired_uses_sqlite_writer_section(monkeypatch) -> None:
    session = MagicMock()
    session.execute = AsyncMock()
    session.commit = AsyncMock()

    order: list[str] = []

    @asynccontextmanager
    async def fake_writer_section():
        order.append("lock-enter")
        yield
        order.append("lock-exit")

    monkeypatch.setattr(oidc_flows_module, "sqlite_writer_section", fake_writer_section)
    repo = OidcFlowRepository(session)
    await repo.purge_expired()
    assert order == ["lock-enter", "lock-exit"]
