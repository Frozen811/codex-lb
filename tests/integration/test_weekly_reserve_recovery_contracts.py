from __future__ import annotations

from datetime import datetime, timezone

import pytest
from sqlalchemy import select

from app.core.config.settings import get_settings
from app.core.utils.time import utcnow
from app.db.models import Account, AccountStatus, StickySession, StickySessionKind, UsageHistory
from app.db.session import SessionLocal
from app.modules.accounts.api import get_proxy_service_for_app
from app.modules.proxy.load_balancer import RuntimeState
from tests.integration.test_accounts_api_probe import _import_test_account

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_manual_resume_clears_persisted_quota_markers(async_client) -> None:
    """The dashboard's existing action atomically clears the quota hold."""
    account_id = await _import_test_account(
        async_client, email="manual-weekly-reserve@example.test", account_id="manual-weekly-reserve"
    )
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        account.status = AccountStatus.QUOTA_EXCEEDED
        account.blocked_at = 2_000_000_000
        account.reset_at = 2_000_086_400
        session.add(StickySession(key="manual-owner", kind=StickySessionKind.STICKY_THREAD, account_id=account_id))
        await session.commit()
    response = await async_client.post(f"/api/accounts/{account_id}/reactivate")
    assert response.status_code == 200, response.text
    assert response.json() == {"status": "reactivated"}
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        assert (account.status, account.blocked_at, account.reset_at) == (AccountStatus.ACTIVE, None, None)
        owner = await session.get(StickySession, ("manual-owner", StickySessionKind.STICKY_THREAD))
        assert owner is not None and owner.account_id == account_id


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize(
    "evidence",
    ["available", "missing", "pre_block", "same_second", "exhausted", "debounce", "rate_limit"],
)
async def test_weekly_primary_recovery_preserves_quota_and_owner_contract(
    async_client, app_instance, monkeypatch, path: str, evidence: str
) -> None:
    """Exercise weekly-only admission through public routes and committed rows."""
    monkeypatch.setenv("CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_ENABLED", "false")
    get_settings.cache_clear()
    account_id = await _import_test_account(
        async_client, email="weekly-reserve@example.test", account_id="weekly-reserve"
    )
    now = utcnow().replace(tzinfo=timezone.utc).timestamp()
    blocked_at = int(now - (10 if evidence == "debounce" else 130))
    reset_at = int(now + 86400)
    status = AccountStatus.RATE_LIMITED if evidence == "rate_limit" else AccountStatus.QUOTA_EXCEEDED
    recorded_at = {
        "pre_block": blocked_at - 1,
        "same_second": blocked_at + 0.5,
    }.get(evidence, now)
    used_percent = 100.0 if evidence == "exhausted" else 87.0
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        account.status = status
        account.blocked_at = blocked_at
        account.reset_at = reset_at
        if evidence != "missing":
            session.add(
                UsageHistory(
                    account_id=account_id,
                    window="primary",
                    window_minutes=10080,
                    used_percent=used_percent,
                    reset_at=reset_at,
                    recorded_at=datetime.fromtimestamp(recorded_at, timezone.utc).replace(tzinfo=None),
                )
            )
        session.add(StickySession(key="weekly-owner", kind=StickySessionKind.STICKY_THREAD, account_id=account_id))
        await session.commit()
    service = get_proxy_service_for_app(app_instance)
    cooldown_until = now + 600 if evidence == "rate_limit" else blocked_at + 120
    runtime = RuntimeState(blocked_at=float(blocked_at), cooldown_until=cooldown_until, reset_at=float(reset_at))
    service._load_balancer._runtime[account_id] = runtime
    dispatched: list[str] = []

    async def stream(payload, headers, access_token, account_id, **kwargs):  # noqa: ARG001
        dispatched.append(account_id)
        yield 'data: {"type":"response.created","response":{"id":"resp_weekly"}}\n\n'
        yield (
            'data: {"type":"response.completed","response":{"id":"resp_weekly",'
            '"object":"response","status":"completed","output":[]}}\n\n'
        )

    monkeypatch.setattr("app.modules.proxy.service.core_stream_responses", stream)
    try:
        response = await async_client.post(
            path,
            headers={"session_id": "weekly-owner"},
            json={"model": "gpt-5.1", "input": "continue", "instructions": "", "stream": True},
        )
        assert response.status_code == (429 if evidence == "exhausted" else 200), response.text
        if evidence == "exhausted":
            assert response.json()["error"]["code"] == "usage_limit_reached"
        if evidence == "available":
            assert "response.completed" in response.text, response.text
            assert dispatched == ["weekly-reserve"]
            assert runtime.blocked_at is None
            assert runtime.cooldown_until is None
            assert runtime.reset_at is None
        else:
            assert "response.completed" not in response.text
            assert dispatched == []
            if evidence == "rate_limit":
                assert runtime.cooldown_until == cooldown_until
                assert runtime.blocked_at == blocked_at
        assert await service.drain_persistence_tasks(5.0)
        async with SessionLocal() as session:
            account = await session.get(Account, account_id)
            assert account is not None
            assert account.status == (AccountStatus.ACTIVE if evidence == "available" else status)
            if evidence == "available":
                assert account.blocked_at is None
                assert account.reset_at is None
            else:
                assert account.blocked_at == blocked_at
                assert account.reset_at == reset_at
            owner = await session.get(StickySession, ("weekly-owner", StickySessionKind.STICKY_THREAD))
            assert owner is not None
            assert owner.account_id == account_id
            assert owner.continuity_abandoned_at is None
            result = await session.execute(select(UsageHistory).where(UsageHistory.account_id == account_id))
            rows = result.scalars().all()
            assert len(rows) == (0 if evidence == "missing" else 1)
            if rows:
                assert (rows[0].window, rows[0].window_minutes, rows[0].used_percent) == (
                    "primary",
                    10080,
                    used_percent,
                )
    finally:
        get_settings.cache_clear()
