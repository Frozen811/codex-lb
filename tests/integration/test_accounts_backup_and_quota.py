from __future__ import annotations

import base64
import json

import pytest

from app.core.auth import generate_unique_account_id

pytestmark = pytest.mark.integration


def _encode_jwt(payload: dict) -> str:
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    body = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    return f"header.{body}.sig"


async def _import_test_account(async_client, *, email: str, account_id: str, plan_type: str = "pro") -> str:
    payload = {
        "email": email,
        "chatgpt_account_id": account_id,
        "https://api.openai.com/auth": {"chatgpt_plan_type": plan_type},
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


@pytest.mark.asyncio
async def test_accounts_backup_export_and_restore_e2e(async_client):
    acc_id = await _import_test_account(
        async_client,
        email="backup-e2e@example.com",
        account_id="acc_backup_e2e",
        plan_type="team",
    )
    # Set alias
    await async_client.put(f"/api/accounts/{acc_id}/alias", json={"alias": "team-backup-alias"})

    # Export
    export_resp = await async_client.post("/api/accounts/backup/export")
    assert export_resp.status_code == 200, export_resp.text
    backup = export_resp.json()
    assert backup["version"] == "1.0"
    assert backup["accountCount"] >= 1
    found = [item for item in backup["accounts"] if item["id"] == acc_id]
    assert len(found) == 1
    item = found[0]
    assert item["email"] == "backup-e2e@example.com"
    assert item["alias"] == "team-backup-alias"
    assert item["tokens"]["access_token"] == "access-token-not-a-real-secret"
    assert item["tokens"]["refresh_token"] == "refresh"

    # Restore
    restore_resp = await async_client.post(
        "/api/accounts/backup/restore",
        json={"accounts": [item], "settingsOverrides": {}},
    )
    assert restore_resp.status_code == 200, restore_resp.text
    res = restore_resp.json()
    assert res["success"] is True, f"Restore failed: {res}"
    assert res["restoredCount"] == 1
    assert res["failedCount"] == 0


@pytest.mark.asyncio
async def test_account_quota_limit_api(async_client):
    acc_id = await _import_test_account(
        async_client,
        email="quota-limit@example.com",
        account_id="acc_quota_limit",
        plan_type="pro",
    )

    # Initial state: None
    get_resp = await async_client.get(f"/api/accounts/{acc_id}/quota-limit")
    assert get_resp.status_code == 200
    assert get_resp.json()["limitPercent"] is None

    # Set quota limit to 65%
    put_resp = await async_client.put(
        f"/api/accounts/{acc_id}/quota-limit",
        json={"limitPercent": 65.0},
    )
    assert put_resp.status_code == 200
    assert put_resp.json()["limitPercent"] == 65.0

    # Verify persisted in GET
    get_resp2 = await async_client.get(f"/api/accounts/{acc_id}/quota-limit")
    assert get_resp2.status_code == 200
    assert get_resp2.json()["limitPercent"] == 65.0

    # Clear limit
    put_resp2 = await async_client.put(
        f"/api/accounts/{acc_id}/quota-limit",
        json={"limitPercent": None},
    )
    assert put_resp2.status_code == 200
    assert put_resp2.json()["limitPercent"] is None

    # Missing account 404
    missing_resp = await async_client.get("/api/accounts/missing-account-id/quota-limit")
    assert missing_resp.status_code == 404
