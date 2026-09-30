from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.db.models import Account
from app.modules.api_keys.service import ApiKeyData
from app.modules.proxy._service.continuity_owner import resolve_continuity_owner_candidate
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
