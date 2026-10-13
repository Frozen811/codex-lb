from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.core.balancer.logic import AccountState, select_account
from app.db.models import AccountStatus
from app.modules.accounts.schemas import AccountBackupItem, AccountBackupRestoreRequest, CodexAuthTokens
from app.modules.accounts.service import AccountsService

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("backoff", [False, True])
@pytest.mark.parametrize("bypass", [False, True])
@pytest.mark.parametrize("cap,used,eligible", [(50, 50, False), (50, 49, True), (0, None, False), (None, 50, True)])
def test_operator_cap_bounds_fallback_and_quota_exemption(backoff, bypass, cap, used, eligible):
    state = AccountState(
        account_id="capped",
        status=AccountStatus.ACTIVE,
        used_percent=used,
        quota_limit_percent=cap,
        error_count=3 if backoff else 0,
        last_error_at=990 if backoff else None,
    )
    result = select_account([state], now=1000, ignore_standard_quota=bypass, hard_owner_pool=True)
    assert (result.account is not None) is eligible


async def test_backup_explicit_metadata_targets_returned_identity():
    service = AccountsService(AsyncMock())
    service.import_account = AsyncMock(return_value=SimpleNamespace(account_id="destination"))
    service.set_account_alias = AsyncMock(return_value=True)
    service.set_routing_policy = AsyncMock(return_value=True)
    service.set_limit_warmup_enabled = AsyncMock(return_value=True)
    service.set_quota_limit = AsyncMock(return_value=True)
    service.pause_account = AsyncMock(return_value=True)
    item = AccountBackupItem(
        id="source",
        email="backup@example.invalid",
        alias=None,
        routing_policy="preserve",
        limit_warmup=False,
        quota_limit_percent=0,
        status="paused",
        tokens=CodexAuthTokens(access_token="test-access", account_id="workspace"),
    )
    result = await service.restore_backup(AccountBackupRestoreRequest(accounts=[item]))
    assert result.success and result.restored_count == 1
    service.set_account_alias.assert_awaited_once_with("destination", None)
    service.set_routing_policy.assert_awaited_once_with("destination", "preserve")
    service.set_limit_warmup_enabled.assert_awaited_once_with("destination", False)
    service.set_quota_limit.assert_awaited_once_with("destination", 0)
    service.pause_account.assert_awaited_once_with("destination")


async def test_older_backup_omitted_metadata_preserves_settings():
    service = AccountsService(AsyncMock())
    service.import_account = AsyncMock(return_value=SimpleNamespace(account_id="destination"))
    service.set_account_alias = AsyncMock()
    service.set_routing_policy = AsyncMock()
    service.set_limit_warmup_enabled = AsyncMock()
    service.set_quota_limit = AsyncMock()
    item = AccountBackupItem(id="source", tokens=CodexAuthTokens(access_token="test-access"))
    result = await service.restore_backup(AccountBackupRestoreRequest(accounts=[item]))
    assert result.success
    for setter in (
        service.set_account_alias,
        service.set_routing_policy,
        service.set_limit_warmup_enabled,
        service.set_quota_limit,
    ):
        setter.assert_not_awaited()
