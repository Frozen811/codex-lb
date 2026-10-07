from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.core.balancer import AccountState, select_account
from app.db.models import AccountStatus
from app.modules.accounts.service import AccountsService


@pytest.mark.parametrize(
    "used,secondary,limit,blocked",
    [
        (45.0, 30.0, 50.0, False),
        (50.0, 30.0, 50.0, True),
        (30.0, 50.0, 50.0, True),
        (None, None, 0.0, True),
        (99.0, 99.0, None, False),
    ],
)
def test_select_account_filters_persisted_quota_restriction(used, secondary, limit, blocked):
    state = AccountState(
        "restricted",
        AccountStatus.ACTIVE,
        used_percent=used,
        secondary_used_percent=secondary,
        quota_limit_percent=limit,
    )
    assert (select_account([state]).account is None) == blocked
    assert select_account([state], ignore_standard_quota=True).account is not None


async def test_service_quota_limit_commits_and_propagates(monkeypatch):
    repo = AsyncMock()
    repo.update_quota_limit.return_value = True
    propagate = AsyncMock()
    monkeypatch.setattr("app.modules.accounts.service.propagate_account_routing_change", propagate)
    service = AccountsService(repo=repo)
    assert await service.set_quota_limit("account", 50.0)
    repo.update_quota_limit.assert_awaited_once_with("account", 50.0)
    propagate.assert_awaited_once()
