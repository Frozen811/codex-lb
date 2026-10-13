from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pytest
from sqlalchemy import select, update

from app.core.clients.rate_limit_reset_credits import (
    RateLimitResetCreditsSnapshot,
    ResetCreditItem,
    ResetCreditsResponse,
)
from app.core.exceptions import DashboardConflictError
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.rate_limit_reset_credits import api as credits_api
from app.modules.rate_limit_reset_credits.store import RateLimitResetCreditsStore
from tests.integration.test_accounts_backup_and_quota import _import_test_account

pytestmark = pytest.mark.integration


async def test_backup_restores_settings_to_credential_identity(async_client):
    account_id = await _import_test_account(async_client, email="portable@example.invalid", account_id="portable")
    async with SessionLocal() as session:
        await session.execute(
            update(Account).where(Account.id == account_id).values(alias="old", limit_warmup_enabled=True)
        )
        await session.commit()
    exported = await async_client.post("/api/accounts/backup/export")
    assert exported.status_code == 200
    assert "no-store" in exported.headers["cache-control"]
    item = next(item for item in exported.json()["accounts"] if item["id"] == account_id)
    item.update(
        id="foreign-source-id",
        alias=None,
        limitWarmup=False,
        quotaLimitPercent=0,
        status="paused",
        routingPolicy="preserve",
    )
    restored = await async_client.post("/api/accounts/backup/restore", json={"accounts": [item]})
    assert restored.status_code == 200, restored.text
    assert restored.json()["success"] is True
    async with SessionLocal() as session:
        account = (await session.execute(select(Account).where(Account.id == account_id))).scalar_one()
        assert account.alias is None
        assert account.limit_warmup_enabled is False
        assert account.quota_limit_percent == 0
        assert account.routing_policy == "preserve"
        assert account.status == AccountStatus.PAUSED
        assert await session.get(Account, "foreign-source-id") is None


async def test_backup_workspace_metadata_round_trip(async_client):
    restored = await async_client.post(
        "/api/accounts/backup/restore",
        json={
            "accounts": [
                {
                    "id": "portable-source",
                    "email": "workspace@example.invalid",
                    "planType": "team",
                    "workspaceId": "test-workspace",
                    "workspaceLabel": "Testing",
                    "seatType": "standard",
                    "tokens": {"access_token": "opaque-test-access", "account_id": "upstream-account"},
                }
            ]
        },
    )
    assert restored.status_code == 200 and restored.json()["success"], restored.text
    exported = await async_client.post("/api/accounts/backup/export")
    item = next(item for item in exported.json()["accounts"] if item["email"] == "workspace@example.invalid")
    assert (item["workspaceId"], item["workspaceLabel"], item["seatType"]) == ("test-workspace", "Testing", "standard")
    repeated = await async_client.post("/api/accounts/backup/restore", json={"accounts": [item]})
    assert repeated.json()["success"]
    async with SessionLocal() as session:
        rows = (
            (await session.execute(select(Account).where(Account.email == "workspace@example.invalid"))).scalars().all()
        )
        assert len(rows) == 1


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_zero_account_cap_blocks_public_response_dispatch(async_client, monkeypatch, path):
    account_id = await _import_test_account(async_client, email="capped@example.invalid", account_id="capped")
    updated = await async_client.put(f"/api/accounts/{account_id}/quota-limit", json={"limitPercent": 0})
    assert updated.status_code == 200
    calls = []

    async def forbidden_stream(*args, **kwargs):
        calls.append(kwargs)
        raise AssertionError("capped account dispatched upstream")
        yield ""

    monkeypatch.setattr("app.modules.proxy.service.core_stream_responses", forbidden_stream)
    response = await async_client.post(path, json={"model": "gpt-5.1-codex-mini", "input": "Hi", "stream": False})
    assert response.status_code == 429, response.text
    assert response.json()["error"]["code"] == "account_usage_limit_reached"
    assert calls == []


async def test_paused_cached_credit_visibility_remains_read_only(async_client, monkeypatch):
    account_id = await _import_test_account(
        async_client, email="paused-credit@example.invalid", account_id="paused-credit"
    )
    store = RateLimitResetCreditsStore()
    expiry = datetime(2030, 1, 1, tzinfo=timezone.utc)
    await store.set(account_id, RateLimitResetCreditsSnapshot(available_count=2, nearest_expires_at=expiry))
    monkeypatch.setattr("app.modules.accounts.mappers.get_rate_limit_reset_credits_store", lambda: store)
    monkeypatch.setattr(credits_api, "get_rate_limit_reset_credits_store", lambda: store)
    assert (await async_client.post(f"/api/accounts/{account_id}/pause")).status_code == 200
    accounts = (await async_client.get("/api/accounts")).json()["accounts"]
    account = next(item for item in accounts if item["accountId"] == account_id)
    assert account["availableResetCredits"] == 2
    assert account["resetCreditNearestExpiresAt"].startswith("2030-01-01")
    result = await async_client.post(
        "/api/accounts/rate-limit-reset-credits/redeem-all", json={"accountIds": [account_id]}
    )
    assert result.status_code == 200
    assert result.json()["totalAccountsAttempted"] == 0
    assert result.json()["results"][0]["success"] is False
    snapshot = store.get(account_id)
    assert snapshot is not None and snapshot.available_count == 2


@pytest.mark.parametrize("partial_failure", [False, True])
async def test_bulk_credits_use_authoritative_remaining_ids_and_keep_partial_counts(
    async_client, monkeypatch, partial_failure
):
    first = await _import_test_account(async_client, email="bulk-a@example.invalid", account_id="bulk-a")
    second = await _import_test_account(async_client, email="bulk-b@example.invalid", account_id="bulk-b")
    store = RateLimitResetCreditsStore()
    await store.set(
        first,
        RateLimitResetCreditsSnapshot(
            available_count=2,
            credits=[ResetCreditItem(id="later", status="available"), ResetCreditItem(id="sooner", status="available")],
        ),
    )
    await store.set(
        second,
        RateLimitResetCreditsSnapshot(available_count=1, credits=[ResetCreditItem(id="other", status="available")]),
    )
    monkeypatch.setattr(credits_api, "get_rate_limit_reset_credits_store", lambda: store)
    calls = []
    fetched = []

    async def fetch_remaining(access_token, upstream_id, **kwargs):
        fetched.append(upstream_id)
        assert access_token == "access-token-not-a-real-secret"
        return ResetCreditsResponse(available_count=1, credits=[ResetCreditItem(id="later", status="available")])

    async def redeem(**kwargs):
        account_id = kwargs["account"].id
        snapshot = store.get(account_id)
        assert snapshot is not None
        credit_ids = [item.id for item in snapshot.credits]
        calls.append((account_id, credit_ids))
        if account_id == first and len([call for call in calls if call[0] == first]) == 2:
            assert credit_ids == ["later"]
            if partial_failure:
                raise DashboardConflictError("synthetic second consume failure", code="test_failure")
            remaining = 0
        else:
            remaining = 1 if account_id == first else 0
        await store.invalidate(account_id)
        return SimpleNamespace(response=SimpleNamespace(windows_reset=1), available_count_after=remaining)

    monkeypatch.setattr(credits_api, "fetch_reset_credits", fetch_remaining)
    monkeypatch.setattr(credits_api, "_redeem_soonest_reset_credit", redeem)
    result = await async_client.post(
        "/api/accounts/rate-limit-reset-credits/redeem-all", json={"accountIds": [first, second]}
    )
    assert result.status_code == 200, result.text
    body = result.json()
    assert body["totalAccountsAttempted"] == body["totalAccountsSucceeded"] == 2
    assert body["totalCreditsRedeemed"] == (2 if partial_failure else 3)
    assert fetched == ["bulk-a"]
    assert len(calls) == 3
    item = next(item for item in body["results"] if item["accountId"] == first)
    assert item["creditsRedeemed"] == (1 if partial_failure else 2)
    assert bool(item["error"]) is partial_failure
