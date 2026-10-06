from __future__ import annotations

import base64
import json
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.core.crypto import TokenEncryptor
from app.core.usage.models import UsagePayload
from app.db.models import Account
from app.db.session import SessionLocal
from app.modules.accounts.auth_manager import AuthManager, RefreshError
from app.modules.accounts.repository import AccountsRepository

pytestmark = pytest.mark.integration


def _auth_file(*, access: str = "synthetic-pat", camel: bool = True, optional: str | None = None) -> dict:
    return {
        "tokens": {
            "accessToken" if camel else "access_token": access,
            "idToken" if camel else "id_token": optional,
            "refreshToken" if camel else "refresh_token": optional,
        },
        "email": "pat@example.com",
        "planType" if camel else "plan_type": "enterprise",
        "accountId" if camel else "account_id": "pat-account",
        "workspaceId" if camel else "workspace_id": "pat-workspace",
        "workspaceLabel" if camel else "workspace_label": "PAT workspace",
    }


async def _import(client, payload: dict):
    return await client.post(
        "/api/accounts/import",
        files={"auth_json": ("auth.json", json.dumps(payload), "application/json")},
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("camel", [True, False])
@pytest.mark.parametrize("optional", [None, "", " \t\n"])
async def test_pat_import_preserves_metadata_and_absent_tokens(async_client, camel, optional):
    response = await _import(async_client, _auth_file(camel=camel, optional=optional))
    assert response.status_code == 200
    imported = response.json()
    assert imported["email"] == "pat@example.com"
    assert imported["planType"] == "enterprise"
    assert imported["workspaceId"] == "pat-workspace"
    assert imported["workspaceLabel"] == "PAT workspace"

    listed = await async_client.get("/api/accounts")
    summary = next(row for row in listed.json()["accounts"] if row["accountId"] == imported["accountId"])
    assert summary["auth"]["refresh"]["state"] == "non_refreshable"
    assert "synthetic-pat" not in listed.text

    encryptor = TokenEncryptor()
    async with SessionLocal() as session:
        row = await session.get(Account, imported["accountId"])
        assert row is not None
        assert row.chatgpt_account_id == "pat-account"
        assert encryptor.decrypt(row.access_token_encrypted) == "synthetic-pat"
        assert encryptor.decrypt(row.refresh_token_encrypted) == ""
        assert encryptor.decrypt(row.id_token_encrypted) == ""
        manager = AuthManager(AccountsRepository(session))
        assert await manager.ensure_fresh(row) is row
        with pytest.raises(RefreshError) as error:
            await manager.ensure_fresh(row, force=True)
        assert error.value.is_permanent
        assert error.value.code == "non_refreshable_account"

    exported = await async_client.post(f"/api/accounts/{imported['accountId']}/export/auth")
    assert exported.status_code == 200
    assert exported.json()["tokens"]["refreshToken"] is None
    assert exported.json()["tokens"]["idToken"] is None


@pytest.mark.asyncio
@pytest.mark.parametrize("access", ["", " \t\n"])
async def test_blank_access_import_is_rejected_before_persistence(async_client, access):
    response = await _import(async_client, _auth_file(access=access))
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "invalid_auth_json"
    assert "synthetic-pat" not in response.text
    async with SessionLocal() as session:
        assert (await session.execute(select(Account))).scalars().all() == []


@pytest.mark.asyncio
async def test_backup_restore_uses_the_same_nonblank_credential_policy(async_client):
    response = await async_client.post(
        "/api/accounts/backup/restore",
        json={
            "accounts": [
                {"id": "invalid", "email": "invalid@example.com", "tokens": {"access_token": " \t"}},
                {
                    "id": "valid",
                    "email": "valid@example.com",
                    "planType": "business",
                    "tokens": {"access_token": "synthetic-pat", "account_id": "restore-pat", "refresh_token": "  "},
                },
            ]
        },
    )
    assert response.status_code == 200
    result = response.json()
    assert (result["restoredCount"], result["failedCount"]) == (1, 1)
    accounts = (await async_client.get("/api/accounts")).json()["accounts"]
    assert len(accounts) == 1
    assert accounts[0]["email"] == "valid@example.com"
    assert accounts[0]["auth"]["refresh"]["state"] == "non_refreshable"


@pytest.mark.asyncio
async def test_expired_access_only_probe_never_dispatches(async_client, monkeypatch):
    encoded = base64.urlsafe_b64encode(b'{"exp":1}').rstrip(b"=").decode()
    response = await _import(async_client, _auth_file(access=f"header.{encoded}.sig"))
    assert response.status_code == 200
    send = AsyncMock(return_value=200)
    monkeypatch.setattr("app.modules.accounts.service.AccountsService._send_probe_request", send)
    probed = await async_client.post(f"/api/accounts/{response.json()['accountId']}/probe")
    assert probed.status_code == 409
    assert probed.json()["error"]["code"] == "account_probe_refresh_failed"
    send.assert_not_awaited()


@pytest.mark.asyncio
async def test_opaque_pat_usage_probe_uses_explicit_upstream_identity(async_client, monkeypatch):
    response = await _import(async_client, _auth_file())
    assert response.status_code == 200
    captured = []

    async def usage(*, access_token, account_id, **kwargs):
        captured.append((access_token, account_id))
        return UsagePayload.model_validate({"rate_limit_reset_credits": {"available_count": 0}})

    async def must_not_refresh(*args, **kwargs):
        raise AssertionError("Access-token-only account cannot exchange a refresh token")

    monkeypatch.setattr("app.modules.accounts.service.fetch_usage", usage)
    monkeypatch.setattr(AuthManager, "_refresh_tokens", must_not_refresh)
    probed = await async_client.get(f"/api/accounts/{response.json()['accountId']}/usage-reset-credits")
    assert probed.status_code == 200
    assert captured == [("synthetic-pat", "pat-account")]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_expired_access_only_response_marks_reauth_without_upstream_io(async_client, monkeypatch, path):
    encoded = base64.urlsafe_b64encode(b'{"exp":1}').rstrip(b"=").decode()
    imported = await _import(async_client, _auth_file(access=f"header.{encoded}.sig"))
    assert imported.status_code == 200
    calls = []

    async def stream(*args, **kwargs):
        calls.append(True)
        yield 'data: {"type":"response.completed"}\n\n'

    monkeypatch.setattr("app.modules.proxy.service.core_stream_responses", stream)
    await async_client.post(path, json={"model": "gpt-5.4", "instructions": "hi", "input": [], "stream": True})
    assert calls == []
    async with SessionLocal() as session:
        row = await session.get(Account, imported.json()["accountId"])
        assert row is not None
        assert row.status.value == "reauth_required"
