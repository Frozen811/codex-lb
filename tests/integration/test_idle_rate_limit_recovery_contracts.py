from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.core.usage.refresh_scheduler import reconcile_recoverable_account_statuses
from app.db.models import Account, AccountStatus, UsageHistory
from app.db.session import SessionLocal
from app.modules.accounts.repository import AccountsRepository
from app.modules.usage.repository import UsageRepository
from tests.integration.test_accounts_api_probe import _import_test_account

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("case", ["elapsed", "future", "exhausted-long", "stale", "concurrent-hold"])
async def test_idle_rate_limit_recovery_is_persisted_and_visible_without_generation(async_client, case: str) -> None:
    account_id = await _import_test_account(
        async_client, email="idle-rate-recovery@example.test", account_id="idle-rate-recovery"
    )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    epoch = int(now.replace(tzinfo=timezone.utc).timestamp())
    recorded_at = now - timedelta(hours=2) if case == "stale" else now
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        account.status = AccountStatus.RATE_LIMITED
        account.blocked_at = epoch - 130
        account.reset_at = epoch + 3600 if case == "future" else epoch - 10
        session.add_all(
            [
                UsageHistory(
                    account_id=account_id,
                    window="primary",
                    used_percent=10.0,
                    reset_at=epoch + 3600,
                    window_minutes=300,
                    recorded_at=recorded_at,
                ),
                UsageHistory(
                    account_id=account_id,
                    window="secondary",
                    used_percent=100.0 if case == "exhausted-long" else 20.0,
                    reset_at=epoch + 7200,
                    window_minutes=10080,
                    recorded_at=recorded_at,
                ),
            ]
        )
        await session.commit()

    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        if case == "concurrent-hold":
            async with SessionLocal() as peer:
                changed = await peer.get(Account, account_id)
                assert changed is not None
                changed.status = AccountStatus.PAUSED
                await peer.commit()
        recovered = await reconcile_recoverable_account_statuses(
            accounts_repo=AccountsRepository(session),
            usage_repo=UsageRepository(session),
            accounts=[account],
        )
    assert recovered == (1 if case == "elapsed" else 0)

    expected = (
        AccountStatus.ACTIVE
        if case == "elapsed"
        else AccountStatus.PAUSED
        if case == "concurrent-hold"
        else AccountStatus.RATE_LIMITED
    )
    async with SessionLocal() as session:
        persisted = await session.get(Account, account_id)
        assert persisted is not None and persisted.status == expected
        if case == "elapsed":
            assert persisted.reset_at is None and persisted.blocked_at is None
    response = await async_client.get("/api/accounts")
    assert response.status_code == 200
    row = next(row for row in response.json()["accounts"] if row["accountId"] == account_id)
    # The dashboard projects observed long-window exhaustion as quota_exceeded;
    # both that view and the persisted rate-limit hold must remain blocked.
    api_expected = AccountStatus.QUOTA_EXCEEDED if case == "exhausted-long" else expected
    assert row["status"] == api_expected.value
