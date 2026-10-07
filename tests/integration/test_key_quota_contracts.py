from __future__ import annotations

import pytest

from app.core.balancer import select_account
from app.core.openai.models import OpenAIResponsePayload
from app.core.utils.time import utcnow
from app.db.models import Account, LimitType, RequestLog
from app.db.session import SessionLocal
from app.modules.api_keys.repository import ApiKeysRepository
from app.modules.proxy.load_balancer import LoadBalancer
from app.modules.usage.repository import UsageRepository
from tests.integration.test_accounts_backup_and_quota import _import_test_account
from tests.integration.test_api_keys_api import _TEST_MODELS, _import_account, proxy_module
from tests.integration.test_load_balancer_integration import _repo_factory

pytestmark = pytest.mark.integration


async def test_credit_display_override_does_not_block_compact_traffic(async_client, monkeypatch):
    await async_client.put("/api/settings", json={"apiKeyAuthEnabled": True})
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "display-only",
            "limits": [
                {"limitType": "credits", "limitWindow": "5h", "maxValue": 1},
                {"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 1_000_000},
            ],
        },
    )
    assert created.status_code == 200
    key = created.json()
    await _import_account(async_client, "acc_credit_display", "credit-display@example.com")
    async with SessionLocal() as session:
        limits = await ApiKeysRepository(session).get_limits_by_key(key["id"])
        credit = next(limit for limit in limits if limit.limit_type == LimitType.CREDITS)
        credit.current_value = 1
        await session.commit()

    async def compact(*args, **kwargs):
        return OpenAIResponsePayload.model_validate(
            {
                "id": "resp_display",
                "model": _TEST_MODELS[0],
                "status": "completed",
                "output": [],
                "usage": {"input_tokens": 70_000, "output_tokens": 30_000, "total_tokens": 100_000},
            }
        )

    monkeypatch.setattr(proxy_module, "core_compact_responses", compact)
    headers = {"Authorization": f"Bearer {key['key']}"}
    response = await async_client.post(
        "/v1/responses/compact",
        headers=headers,
        json={"model": _TEST_MODELS[0], "instructions": "hello", "input": []},
    )
    assert response.status_code == 200, response.text
    usage = await async_client.get("/v1/usage", headers=headers)
    assert usage.status_code == 200
    by_type = {limit["limit_type"]: limit for limit in usage.json()["limits"]}
    assert by_type["credits"]["current_value"] == 1
    assert by_type["total_tokens"]["current_value"] == 100_000


@pytest.mark.parametrize("limit", [0.0, 50.0, None])
async def test_quota_limit_is_persisted_and_used_by_fresh_selection(async_client, limit):
    account_id = await _import_test_account(async_client, email="durable@example.com", account_id="durable")
    response = await async_client.put(f"/api/accounts/{account_id}/quota-limit", json={"limitPercent": limit})
    assert response.status_code == 200
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        assert account.quota_limit_percent == limit
        state = LoadBalancer(_repo_factory)._state_for(account)
        state.used_percent = 50.0 if limit else None
        selection = select_account([state], ignore_standard_quota=False)
        assert (selection.account is None) == (limit is not None)
        assert select_account([state], ignore_standard_quota=True).account is not None


async def test_explicit_usage_reset_preserves_key_and_history(async_client):
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "stable identity",
            "allowedModels": [_TEST_MODELS[0]],
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 1000}],
        },
    )
    assert created.status_code == 200
    key = created.json()
    async with SessionLocal() as session:
        before = await ApiKeysRepository(session).get_by_id(key["id"])
        assert before is not None
        key_hash = before.key_hash
        limits = await ApiKeysRepository(session).get_limits_by_key(key["id"])
        limits[0].current_value = 111
        session.add(
            RequestLog(
                api_key_id=key["id"],
                request_id="reset-history",
                model=_TEST_MODELS[0],
                status="success",
                input_tokens=111,
                output_tokens=0,
                requested_at=utcnow(),
            )
        )
        await session.commit()
    reset = await async_client.patch(f"/api/api-keys/{key['id']}", json={"resetUsage": True})
    assert reset.status_code == 200
    assert reset.json()["limits"][0]["currentValue"] == 0
    for field in ("id", "name", "keyPrefix", "allowedModels", "isActive"):
        assert reset.json()[field] == key[field]
    async with SessionLocal() as session:
        after = await ApiKeysRepository(session).get_by_id(key["id"])
        assert after is not None and after.key_hash == key_hash
    history = await async_client.get(f"/api/api-keys/{key['id']}/usage")
    assert history.status_code == 200 and history.json()["totalTokens"] == 111


async def test_quota_limit_changes_reach_an_existing_balancer(async_client):
    account_id = await _import_test_account(async_client, email="live-limit@example.com", account_id="live-limit")
    async with SessionLocal() as session:
        await UsageRepository(session).add_entry(account_id, 55.0, window="primary", window_minutes=300)
    balancer = LoadBalancer(_repo_factory)
    assert (await balancer.select_account(account_ids={account_id})).account is not None
    response = await async_client.put(f"/api/accounts/{account_id}/quota-limit", json={"limitPercent": 50})
    assert response.status_code == 200
    assert (await balancer.select_account(account_ids={account_id})).account is None
    response = await async_client.put(f"/api/accounts/{account_id}/quota-limit", json={"limitPercent": None})
    assert response.status_code == 200
    assert (await balancer.select_account(account_ids={account_id})).account is not None


async def test_quota_limit_backup_restore_round_trip(async_client):
    account_id = await _import_test_account(async_client, email="quota-backup@example.com", account_id="quota-backup")
    response = await async_client.put(f"/api/accounts/{account_id}/quota-limit", json={"limitPercent": 50})
    assert response.status_code == 200
    backup = await async_client.post("/api/accounts/backup/export")
    assert backup.status_code == 200
    item = next(item for item in backup.json()["accounts"] if item["id"] == account_id)
    assert item["quotaLimitPercent"] == 50
    await async_client.put(f"/api/accounts/{account_id}/quota-limit", json={"limitPercent": None})
    restored = await async_client.post("/api/accounts/backup/restore", json={"accounts": [item]})
    assert restored.status_code == 200 and restored.json()["success"]
    assert (await async_client.get(f"/api/accounts/{account_id}/quota-limit")).json()["limitPercent"] == 50
    item.pop("quotaLimitPercent")
    legacy_restore = await async_client.post("/api/accounts/backup/restore", json={"accounts": [item]})
    assert legacy_restore.status_code == 200 and legacy_restore.json()["success"]
    assert (await async_client.get(f"/api/accounts/{account_id}/quota-limit")).json()["limitPercent"] == 50
