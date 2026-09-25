from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from app.core.balancer import AccountState, select_account
from app.db.models import AccountStatus
from app.modules.accounts.quota_restriction import (
    clear_account_quota_restrictions,
    get_account_quota_restriction,
    is_account_quota_restricted,
    set_account_quota_restriction,
)
from app.modules.accounts.service import AccountsService


@pytest.fixture(autouse=True)
def _clean_quota_restrictions():
    clear_account_quota_restrictions()
    yield
    clear_account_quota_restrictions()


def test_quota_restriction_registry():
    account_id = "test-acc-1"
    assert get_account_quota_restriction(account_id) is None
    assert is_account_quota_restricted(account_id, 80.0, 90.0) is False

    set_account_quota_restriction(account_id, 50.0)
    assert get_account_quota_restriction(account_id) == 50.0

    # Under limit
    assert is_account_quota_restricted(account_id, 45.0, 30.0) is False
    # Primary over limit
    assert is_account_quota_restricted(account_id, 55.0, 30.0) is True
    # Secondary over limit
    assert is_account_quota_restricted(account_id, 30.0, 52.0) is True

    # Clear limit
    set_account_quota_restriction(account_id, None)
    assert get_account_quota_restriction(account_id) is None
    assert is_account_quota_restricted(account_id, 99.0, 99.0) is False


def test_select_account_filters_quota_restricted():
    set_account_quota_restriction("acc-restricted", 40.0)

    states = [
        AccountState("acc-restricted", AccountStatus.ACTIVE, used_percent=50.0),
        AccountState("acc-available", AccountStatus.ACTIVE, used_percent=80.0),
    ]

    # Without bypass: restricted account is filtered out even though it has lower usage than 80%
    result = select_account(states, routing_strategy="usage_weighted", ignore_standard_quota=False)
    assert result.account is not None
    assert result.account.account_id == "acc-available"

    # With bypass: restricted account is eligible
    result_bypass = select_account(states, routing_strategy="usage_weighted", ignore_standard_quota=True)
    assert result_bypass.account is not None
    assert result_bypass.account.account_id == "acc-restricted"


def test_service_quota_limit_delegation():
    repo = AsyncMock()
    service = AccountsService(repo=repo)

    assert service.get_quota_limit("acc-x") is None
    service.set_quota_limit("acc-x", 75.0)
    assert service.get_quota_limit("acc-x") == 75.0
    service.set_quota_limit("acc-x", None)
    assert service.get_quota_limit("acc-x") is None
