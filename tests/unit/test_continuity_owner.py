from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from sqlalchemy import inspect
from sqlalchemy.orm.exc import DetachedInstanceError

from app.core.utils.time import utcnow
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.dependencies import _proxy_repo_context
from app.modules.accounts.repository import AccountsRepository
from app.modules.api_keys.service import ApiKeyData
from app.modules.proxy._service.support import resolve_continuity_owner_candidate
from app.modules.proxy.load_balancer import LoadBalancer

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
async def test_list_continuity_owner_candidates_unscoped():
    mock_repo = MagicMock()
    acc1 = Account(id="acc-1", email="acc1@example.com")
    acc2 = Account(id="acc-2", email="acc2@example.com")
    mock_repo.accounts.list_accounts = AsyncMock(return_value=[acc1, acc2])

    class MockRepoFactory:
        def __call__(self):
            return self

        async def __aenter__(self):
            return mock_repo

        async def __aexit__(self, *args):
            return None

    lb = LoadBalancer(MockRepoFactory())
    candidates = await lb.list_continuity_owner_candidates()
    assert [a.id for a in candidates] == ["acc-1", "acc-2"]


@pytest.mark.asyncio
async def test_list_continuity_owner_candidates_scoped_key():
    mock_repo = MagicMock()
    acc1 = Account(id="acc-1", email="acc1@example.com")
    acc2 = Account(id="acc-2", email="acc2@example.com")
    mock_repo.accounts.list_accounts = AsyncMock(return_value=[acc1, acc2])

    class MockRepoFactory:
        def __call__(self):
            return self

        async def __aenter__(self):
            return mock_repo

        async def __aexit__(self, *args):
            return None

    lb = LoadBalancer(MockRepoFactory())
    api_key = MagicMock(spec=ApiKeyData)
    api_key.account_assignment_scope_enabled = True
    api_key.assigned_account_ids = ["acc-2"]

    candidates = await lb.list_continuity_owner_candidates(api_key=api_key)
    assert [a.id for a in candidates] == ["acc-2"]


@pytest.mark.asyncio
async def test_resolve_continuity_owner_candidate_single_account():
    lb = MagicMock(spec=LoadBalancer)
    acc1 = Account(id="acc-1", email="acc1@example.com")
    lb.list_continuity_owner_candidates = AsyncMock(return_value=[acc1])

    result = await resolve_continuity_owner_candidate(lb)
    assert result == "acc-1"


@pytest.mark.asyncio
async def test_resolve_continuity_owner_candidate_multiple_accounts_returns_none():
    lb = MagicMock(spec=LoadBalancer)
    acc1 = Account(id="acc-1", email="acc1@example.com")
    acc2 = Account(id="acc-2", email="acc2@example.com")
    lb.list_continuity_owner_candidates = AsyncMock(return_value=[acc1, acc2])

    result = await resolve_continuity_owner_candidate(lb)
    assert result is None


@pytest.mark.asyncio
async def test_resolve_continuity_owner_candidate_zero_accounts_returns_none():
    lb = MagicMock(spec=LoadBalancer)
    lb.list_continuity_owner_candidates = AsyncMock(return_value=[])

    result = await resolve_continuity_owner_candidate(lb)
    assert result is None


@pytest.mark.asyncio
async def test_resolve_continuity_owner_candidate_exception_fails_closed():
    lb = MagicMock(spec=LoadBalancer)
    lb.list_continuity_owner_candidates = AsyncMock(side_effect=RuntimeError("db error"))

    result = await resolve_continuity_owner_candidate(lb)
    assert result is None


@pytest.mark.asyncio
async def test_list_continuity_owner_candidates_returns_detached_safe_clones():
    """The rows outlive the repo session, so they must be clones: reading an
    attribute of a detached ORM row raised DetachedInstanceError (owner-miss 500)."""
    mock_repo = MagicMock()
    acc1 = Account(id="acc-1", email="acc1@example.com")
    mock_repo.accounts.list_accounts = AsyncMock(return_value=[acc1])

    class MockRepoFactory:
        def __call__(self):
            return self

        async def __aenter__(self):
            return mock_repo

        async def __aexit__(self, *args):
            return None

    candidates = await LoadBalancer(MockRepoFactory()).list_continuity_owner_candidates()

    assert [candidate.id for candidate in candidates] == ["acc-1"]
    assert candidates[0] is not acc1


@pytest.mark.asyncio
@pytest.mark.parametrize("assigned_ids", [None, ["acc-2"], []])
async def test_candidate_snapshots_survive_real_repository_teardown(db_setup, monkeypatch, assigned_ids):
    async with SessionLocal() as session:
        session.add_all(
            Account(
                id=account_id,
                email=f"{account_id}@example.com",
                plan_type="plus",
                access_token_encrypted=b"access",
                refresh_token_encrypted=b"refresh",
                id_token_encrypted=b"id",
                last_refresh=utcnow(),
                status=status,
            )
            for account_id, status in (("acc-1", AccountStatus.ACTIVE), ("acc-2", AccountStatus.PAUSED))
        )
        await session.commit()

    source_rows: list[Account] = []
    original_list = AccountsRepository.list_accounts

    async def capture_rows(repository):
        rows = await original_list(repository)
        source_rows.extend(rows)
        return rows

    monkeypatch.setattr(AccountsRepository, "list_accounts", capture_rows)
    api_key = None
    if assigned_ids is not None:
        api_key = MagicMock(spec=ApiKeyData)
        api_key.account_assignment_scope_enabled = True
        api_key.assigned_account_ids = assigned_ids

    candidates = await LoadBalancer(_proxy_repo_context).list_continuity_owner_candidates(api_key=api_key)

    assert len(source_rows) == 2
    assert all(inspect(row).detached and inspect(row).expired_attributes for row in source_rows)
    with pytest.raises(DetachedInstanceError):
        _ = source_rows[0].id
    expected_ids = {"acc-1", "acc-2"} if assigned_ids is None else set(assigned_ids)
    assert {candidate.id for candidate in candidates} == expected_ids
    assert all(inspect(candidate).transient for candidate in candidates)
    assert {candidate.status for candidate in candidates} == (
        {AccountStatus.ACTIVE, AccountStatus.PAUSED}
        if assigned_ids is None
        else {AccountStatus.PAUSED}
        if assigned_ids
        else set()
    )


@pytest.mark.asyncio
async def test_resolve_candidate_attribute_failure_fails_closed():
    candidate = MagicMock(spec=Account)
    type(candidate).id = PropertyMock(side_effect=DetachedInstanceError("expired candidate"))
    lb = MagicMock(spec=LoadBalancer)
    lb.list_continuity_owner_candidates = AsyncMock(return_value=[candidate])

    assert await resolve_continuity_owner_candidate(lb) is None
