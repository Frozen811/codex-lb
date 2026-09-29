from __future__ import annotations

import base64
import json
import time
from datetime import datetime
from typing import Any

import pytest
from sqlalchemy import update

from app.core.auth import generate_unique_account_id
from app.core.balancer import PERMANENT_FAILURE_CODES
from app.core.clients.rate_limit_reset_credits import (
    ConsumeResetCreditResponse,
    RateLimitResetCreditsSnapshot,
    ResetCreditItem,
    ResetCreditsResponse,
)
from app.core.crypto import TokenEncryptor
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.rate_limit_reset_credits import api as reset_credits_api
from app.modules.rate_limit_reset_credits.store import get_rate_limit_reset_credits_store

pytestmark = pytest.mark.integration


def _encode_jwt(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    body = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return f"header.{body}.sig"


async def _import_test_account(async_client, *, email: str, account_id: str) -> str:
    payload = {
        "email": email,
        "chatgpt_account_id": account_id,
        "https://api.openai.com/auth": {"chatgpt_plan_type": "plus"},
    }
    auth_json = {
        "tokens": {
            "idToken": _encode_jwt(payload),
            "accessToken": "access-token-not-a-real-secret",
            "refreshToken": "refresh",
            "accountId": account_id,
        },
    }
    files = {"auth_json": ("auth.json", json.dumps(auth_json), "application/json")}
    response = await async_client.post("/api/accounts/import", files=files)
    assert response.status_code == 200, response.text
    return generate_unique_account_id(account_id, email)


def _credit(credit_id: str, *, expires_at: str = "2026-07-12T00:00:00Z") -> ResetCreditItem:
    return ResetCreditItem.model_validate({"id": credit_id, "status": "available", "expires_at": expires_at})


def _upstream_response(credits: list[ResetCreditItem], available_count: int | None = None) -> ResetCreditsResponse:
    count = available_count if available_count is not None else len(credits)
    return ResetCreditsResponse(credits=credits, available_count=count)


def _snapshot(credits: list[ResetCreditItem], available_count: int | None = None) -> RateLimitResetCreditsSnapshot:
    available = available_count if available_count is not None else len(credits)
    expiries = [
        credit.expires_at for credit in credits if credit.status == "available" and credit.expires_at is not None
    ]
    return RateLimitResetCreditsSnapshot(
        available_count=available,
        nearest_expires_at=min(expiries) if expiries else None,
        credits=credits,
    )


@pytest.mark.asyncio
async def test_paused_account_cached_credits_remain_visible_without_upstream(async_client, monkeypatch) -> None:
    account_id = await _import_test_account(
        async_client,
        email="paused-observation@example.com",
        account_id="acc_paused_observation",
    )
    store = get_rate_limit_reset_credits_store()
    await store.set(account_id, _snapshot([_credit("last-observed")], available_count=2))
    assert (await async_client.post(f"/api/accounts/{account_id}/pause")).status_code == 200

    async def should_not_fetch(*args: Any, **kwargs: Any) -> ResetCreditsResponse:
        raise AssertionError("cached observation must not fetch or redeem upstream")

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", should_not_fetch)
    monkeypatch.setattr(reset_credits_api, "consume_reset_credit", should_not_fetch)
    response = await async_client.get(f"/api/accounts/{account_id}/rate-limit-reset-credits")
    assert response.status_code == 200
    assert response.json()["availableCount"] == 2
    assert store.get(account_id) is not None

    response = await async_client.get("/api/accounts")
    account = next(row for row in response.json()["accounts"] if row["accountId"] == account_id)
    assert account["status"] == "paused"
    assert account["availableResetCredits"] == 2
    assert account["resetCreditNearestExpiresAt"] is not None

    for endpoint in ("usage-reset-credits", "rate-limit-reset-credits"):
        response = await async_client.post(f"/api/accounts/{account_id}/{endpoint}/consume")
        assert response.status_code == 409


@pytest.mark.asyncio
async def test_consume_paused_account_returns_409(async_client, monkeypatch) -> None:
    async def _should_not_fetch(*args: Any, **kwargs: Any) -> ResetCreditsResponse:
        raise AssertionError("paused account should not invoke upstream fetch")

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _should_not_fetch)

    account_id = await _import_test_account(
        async_client,
        email="reset-paused@example.com",
        account_id="acc_reset_paused",
    )
    pause_resp = await async_client.post(f"/api/accounts/{account_id}/pause")
    assert pause_resp.status_code == 200

    response = await async_client.post(f"/api/accounts/{account_id}/rate-limit-reset-credits/consume")
    assert response.status_code == 409
    body = response.json()
    assert body["error"]["code"] == "account_not_reset_credit_applicable"


@pytest.mark.asyncio
@pytest.mark.parametrize("credential_state", ["active", "valid", "unknown"])
async def test_consume_usable_account_returns_success_with_mocked_upstream(
    async_client, monkeypatch, credential_state: str
) -> None:
    captured: dict[str, Any] = {}

    async def _fake_fetch(access_token: str, account_id: str | None, **kwargs: Any) -> ResetCreditsResponse:
        captured["fetch_account_id"] = account_id
        captured["fetch_had_token"] = bool(access_token)
        return _upstream_response([_credit("credit-1")])

    async def _fake_consume(
        access_token: str,
        account_id: str | None,
        credit_id: str,
        redeem_request_id: str | None = None,
        **kwargs: Any,
    ) -> ConsumeResetCreditResponse:
        captured.update(
            {
                "consume_account_id": account_id,
                "consume_credit_id": credit_id,
                "redeem_request_id": redeem_request_id,
                "consume_had_token": bool(access_token),
            }
        )
        return ConsumeResetCreditResponse.model_validate(
            {
                "code": "reset",
                "credit": {
                    "id": credit_id,
                    "status": "redeemed",
                    "redeemed_at": "2026-06-13T13:12:31Z",
                },
                "windows_reset": 2,
            }
        )

    async def _noop_refresh(account) -> None:  # noqa: ANN001
        return None

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _fake_fetch)
    monkeypatch.setattr(reset_credits_api, "consume_reset_credit", _fake_consume)
    monkeypatch.setattr(reset_credits_api, "_build_refresh_usage_callback", lambda _context: _noop_refresh)

    account_id = await _import_test_account(
        async_client,
        email="reset-active@example.com",
        account_id="acc_reset_active",
    )
    if credential_state != "active":
        access_token = _encode_jwt({"exp": time.time() + 3600}) if credential_state == "valid" else "opaque"
        async with SessionLocal() as session:
            await session.execute(
                update(Account)
                .where(Account.id == account_id)
                .values(
                    status=AccountStatus.REAUTH_REQUIRED,
                    deactivation_reason=PERMANENT_FAILURE_CODES["refresh_token_invalidated"],
                    access_token_encrypted=TokenEncryptor().encrypt(access_token),
                )
            )
            await session.commit()

    await get_rate_limit_reset_credits_store().set(account_id, _snapshot([_credit("credit-1")]))

    response = await async_client.post(
        f"/api/accounts/{account_id}/rate-limit-reset-credits/consume",
        json={"redeemRequestId": " dashboard-retry-id "},
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["code"] == "reset"
    assert body["windowsReset"] == 2
    assert body["redeemedAt"] is not None
    assert datetime.fromisoformat(body["redeemedAt"].replace("Z", "+00:00")).year == 2026

    assert captured["fetch_account_id"] == "acc_reset_active"
    assert captured["fetch_had_token"] is True
    assert captured["consume_account_id"] == "acc_reset_active"
    assert captured["consume_credit_id"] == "credit-1"
    assert captured["redeem_request_id"] == "dashboard-retry-id"
    assert captured["consume_had_token"] is True


@pytest.mark.asyncio
async def test_consume_without_cached_snapshot_returns_409_without_fetch(async_client, monkeypatch) -> None:
    async def _should_not_fetch(*args: Any, **kwargs: Any) -> ResetCreditsResponse:
        raise AssertionError("uncached consume should not invoke upstream fetch")

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _should_not_fetch)

    account_id = await _import_test_account(
        async_client,
        email="reset-no-cache@example.com",
        account_id="acc_reset_no_cache",
    )

    response = await async_client.post(f"/api/accounts/{account_id}/rate-limit-reset-credits/consume")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "no_available_reset_credit"


@pytest.mark.asyncio
@pytest.mark.parametrize("credential_state", ["expired", "rejected"])
async def test_consume_unavailable_reauth_account_returns_409(async_client, monkeypatch, credential_state: str) -> None:
    async def _should_not_fetch(*args: Any, **kwargs: Any) -> ResetCreditsResponse:
        raise AssertionError("reauth account should not invoke upstream fetch")

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _should_not_fetch)

    account_id = await _import_test_account(
        async_client,
        email="reset-reauth@example.com",
        account_id="acc_reset_reauth",
    )

    async with SessionLocal() as session:
        await session.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(
                status=AccountStatus.REAUTH_REQUIRED,
                deactivation_reason=PERMANENT_FAILURE_CODES[
                    "account_auth_invalidated" if credential_state == "rejected" else "refresh_token_invalidated"
                ],
                access_token_encrypted=TokenEncryptor().encrypt(
                    _encode_jwt({"exp": time.time() + (-60 if credential_state == "expired" else 3600)})
                ),
            )
        )
        await session.commit()

    response = await async_client.post(f"/api/accounts/{account_id}/rate-limit-reset-credits/consume")
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "account_not_reset_credit_applicable"


@pytest.mark.asyncio
async def test_get_returns_null_on_cache_miss_without_upstream_fetch(async_client, monkeypatch) -> None:
    account_id = await _import_test_account(
        async_client,
        email="reset-get@example.com",
        account_id="acc_reset_get",
    )

    async def _should_not_fetch(*args: Any, **kwargs: Any) -> ResetCreditsResponse:
        raise AssertionError("cache-miss GET should not invoke upstream fetch")

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _should_not_fetch)

    response = await async_client.get(f"/api/accounts/{account_id}/rate-limit-reset-credits")
    assert response.status_code == 200, response.text
    assert response.json() is None


@pytest.mark.asyncio
async def test_redeem_all_consumes_eligible_credits_across_accounts(
    async_client,
    monkeypatch,
) -> None:
    redeemed_credits: list[tuple[str, str]] = []

    async def _fake_fetch(access_token: str, account_id: str | None, **kwargs: Any) -> ResetCreditsResponse:
        # Return remaining credits based on what's been redeemed
        account_credits = [c for a, c in redeemed_credits if a == account_id]
        if account_id == "acc_bulk_1":
            all_c = [_credit("c1-1")]
        elif account_id == "acc_bulk_2":
            all_c = [_credit("c2-1"), _credit("c2-2")]
        else:
            all_c = [_credit("c3-1")]
        available = [c for c in all_c if c.id not in account_credits]
        return _upstream_response(available, len(available))

    async def _fake_consume(
        access_token: str,
        account_id: str | None,
        credit_id: str,
        redeem_request_id: str | None = None,
        **kwargs: Any,
    ) -> ConsumeResetCreditResponse:
        redeemed_credits.append((account_id or "", credit_id))
        return ConsumeResetCreditResponse.model_validate(
            {
                "code": "reset",
                "credit": {
                    "id": credit_id,
                    "status": "redeemed",
                    "redeemed_at": "2026-06-13T13:12:31Z",
                },
                "windows_reset": 1,
            }
        )

    async def _noop_refresh(account) -> None:  # noqa: ANN001
        return None

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _fake_fetch)
    monkeypatch.setattr(reset_credits_api, "consume_reset_credit", _fake_consume)
    monkeypatch.setattr(reset_credits_api, "_build_refresh_usage_callback", lambda _context: _noop_refresh)

    acc1 = await _import_test_account(async_client, email="bulk1@example.com", account_id="acc_bulk_1")
    acc2 = await _import_test_account(async_client, email="bulk2@example.com", account_id="acc_bulk_2")
    acc3 = await _import_test_account(async_client, email="bulk3@example.com", account_id="acc_bulk_3")

    # Set acc3 to PAUSED
    async with SessionLocal() as session:
        await session.execute(
            update(Account).where(Account.id == acc3).values(status=AccountStatus.PAUSED)
        )
        await session.commit()

    store = get_rate_limit_reset_credits_store()
    await store.set(acc1, _snapshot([_credit("c1-1")], available_count=1))
    await store.set(acc2, _snapshot([_credit("c2-1"), _credit("c2-2")], available_count=2))
    await store.set(acc3, _snapshot([_credit("c3-1")], available_count=1))

    response = await async_client.post("/api/accounts/rate-limit-reset-credits/redeem-all")
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["totalAccountsAttempted"] == 2
    assert data["totalAccountsSucceeded"] == 2
    assert data["totalCreditsRedeemed"] == 3
    result_ids = {r["accountId"] for r in data["results"]}
    assert acc1 in result_ids
    assert acc2 in result_ids
    assert acc3 not in result_ids

    # Store for acc1 and acc2 should be invalidated
    assert store.get(acc1) is None
    assert store.get(acc2) is None


@pytest.mark.asyncio
async def test_redeem_all_with_explicit_account_ids_and_partial_failure(
    async_client,
    monkeypatch,
) -> None:
    async def _fake_fetch(access_token: str, account_id: str | None, **kwargs: Any) -> ResetCreditsResponse:
        return _upstream_response([_credit(f"{account_id}-c1")], 1)

    async def _fake_consume(
        access_token: str,
        account_id: str | None,
        credit_id: str,
        redeem_request_id: str | None = None,
        **kwargs: Any,
    ) -> ConsumeResetCreditResponse:
        if "fail" in str(account_id):
            raise reset_credits_api.ConsumeResetCreditError("Upstream rejected consume", code="upstream_fail")
        return ConsumeResetCreditResponse.model_validate(
            {
                "code": "reset",
                "credit": {
                    "id": credit_id,
                    "status": "redeemed",
                    "redeemed_at": "2026-06-13T13:12:31Z",
                },
                "windows_reset": 1,
            }
        )

    async def _noop_refresh(account) -> None:  # noqa: ANN001
        return None

    monkeypatch.setattr(reset_credits_api, "fetch_reset_credits", _fake_fetch)
    monkeypatch.setattr(reset_credits_api, "consume_reset_credit", _fake_consume)
    monkeypatch.setattr(reset_credits_api, "_build_refresh_usage_callback", lambda _context: _noop_refresh)

    acc_ok = await _import_test_account(async_client, email="bulkok@example.com", account_id="acc_bulk_ok")
    acc_fail = await _import_test_account(async_client, email="bulkfail@example.com", account_id="acc_bulk_fail")

    store = get_rate_limit_reset_credits_store()
    await store.set(acc_ok, _snapshot([_credit("ok-c1")], available_count=1))
    await store.set(acc_fail, _snapshot([_credit("fail-c1")], available_count=1))

    response = await async_client.post(
        "/api/accounts/rate-limit-reset-credits/redeem-all",
        json={"accountIds": [acc_ok, acc_fail]},
    )
    assert response.status_code == 200, response.text
    data = response.json()

    assert data["totalAccountsAttempted"] == 2
    assert data["totalAccountsSucceeded"] == 1
    assert data["totalCreditsRedeemed"] == 1

    ok_result = next(r for r in data["results"] if r["accountId"] == acc_ok)
    fail_result = next(r for r in data["results"] if r["accountId"] == acc_fail)

    assert ok_result["success"] is True
    assert ok_result["creditsRedeemed"] == 1
    assert fail_result["success"] is False
    assert fail_result["creditsRedeemed"] == 0
    assert fail_result["error"] is not None

