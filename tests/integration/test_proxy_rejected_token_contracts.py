from __future__ import annotations

import base64
import json

import pytest
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.auth.refresh import RefreshError
from app.core.balancer import PERMANENT_FAILURE_CODES
from app.core.clients.proxy import ProxyResponseError
from app.core.crypto import TokenEncryptor
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.accounts import auth_manager as auth_manager_module
from app.modules.accounts.auth_manager import AuthManager
from app.modules.accounts.repository import AccountsRepository
from app.modules.proxy.account_cache import get_account_selection_cache

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _clear_refresh_state():
    auth_manager_module._clear_refresh_singleflight_state()
    yield
    auth_manager_module._clear_refresh_singleflight_state()


async def _create_pool(client, *, refreshable: bool) -> list[str]:
    settings = await client.put("/api/settings", json={"importWithoutOverwrite": False})
    assert settings.status_code == 200
    encoded = base64.urlsafe_b64encode(b'{"exp":4102444800}').rstrip(b"=").decode()
    ids = []
    for suffix in ("a", "b"):
        response = await client.post(
            "/api/accounts/import",
            files={
                "auth_json": (
                    "auth.json",
                    json.dumps(
                        {
                            "email": f"rejection-{suffix}@example.com",
                            "planType": "plus",
                            "accountId": f"rejection-{suffix}",
                            "tokens": {
                                "accessToken": f"header.{encoded}.sig",
                                "refreshToken": "dead-refresh" if refreshable else None,
                            },
                        }
                    ),
                    "application/json",
                )
            },
        )
        assert response.status_code == 200
        ids.append(response.json()["accountId"])
    return ids


def _completion() -> str:
    return (
        'data: {"type":"response.completed","response":{"id":"resp_healthy",'
        '"status":"completed","output":[],"usage":{"input_tokens":2,"output_tokens":1}}}\n\n'
    )


def _revocation() -> str:
    return (
        'data: {"type":"response.failed","response":{"id":"resp_rejected","status":"failed",'
        '"error":{"code":"token_revoked","type":"authentication_error",'
        '"message":"Synthetic access rejection"}}}\n\n'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("code", ["token_expired", "token_revoked"])
@pytest.mark.parametrize("refreshable", [False, True])
@pytest.mark.parametrize("initial_warning", [False, True], ids=["active", "reauth"])
async def test_rejected_generation_fails_over_and_stays_excluded(
    async_client, monkeypatch, path, code, refreshable, initial_warning
):
    account_ids = await _create_pool(async_client, refreshable=refreshable)
    if initial_warning:
        async with SessionLocal() as session:
            repo = AccountsRepository(session)
            for account_id in account_ids:
                await repo.update_status(
                    account_id, AccountStatus.REAUTH_REQUIRED, PERMANENT_FAILURE_CODES["token_expired"]
                )
        get_account_selection_cache().invalidate()
    calls: list[str] = []
    refresh_calls: list[str] = []
    rejected_owner: str | None = None

    async def reject_refresh(self, token, *, account):
        refresh_calls.append(account.id)
        raise RefreshError("refresh_token_invalidated", "Synthetic refresh rejection", True)

    async def stream(payload, headers, access_token, account_id, **kwargs):
        nonlocal rejected_owner
        if rejected_owner is None:
            rejected_owner = account_id
        calls.append(account_id)
        if account_id == rejected_owner:
            if code == "token_expired":
                raise ProxyResponseError(401, {"error": {"code": code, "message": "Synthetic access rejection"}})
            yield _revocation()
            return
        yield _completion()

    monkeypatch.setattr(AuthManager, "_refresh_tokens", reject_refresh)
    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    request = {
        "model": "gpt-5.4",
        "instructions": "hi",
        "input": [],
        "stream": True,
        "prompt_cache_key": "rejection-contract",
    }
    first = await async_client.post(path, json=request)
    assert first.status_code == 200
    assert '"resp_healthy"' in first.text
    assert len(calls) == 2
    assert calls[0] != calls[1]
    assert rejected_owner is not None
    assert len(refresh_calls) == (1 if refreshable and code == "token_expired" and not initial_warning else 0)

    async with SessionLocal() as session:
        rows = (await session.execute(select(Account))).scalars().all()
        rejected = next(row for row in rows if row.chatgpt_account_id == rejected_owner)
        assert rejected.status == AccountStatus.REAUTH_REQUIRED
        expected = "account_auth_invalidated" if code == "token_expired" else "token_revoked"
        assert rejected.deactivation_reason == PERMANENT_FAILURE_CODES[expected]
        rejected_id = rejected.id

    for _ in range(2):
        again = await async_client.post(path, json=request)
        assert again.status_code == 200
        assert '"resp_healthy"' in again.text
    assert calls.count(rejected_owner) == 1

    # Actual credential re-import clears the block on the same identity slot.
    repaired = await async_client.post(
        "/api/accounts/import",
        files={
            "auth_json": (
                "auth.json",
                json.dumps(
                    {
                        "email": rejected.email,
                        "planType": "plus",
                        "accountId": rejected_owner,
                        "tokens": {"accessToken": "synthetic-rotated-access"},
                    }
                ),
                "application/json",
            )
        },
    )
    assert repaired.status_code == 200
    assert repaired.json()["accountId"] == rejected_id
    async with SessionLocal() as session:
        row = await session.get(Account, rejected_id)
        assert row is not None and row.status == AccountStatus.ACTIVE
        assert row.deactivation_reason is None
        assert TokenEncryptor().decrypt(row.access_token_encrypted) == "synthetic-rotated-access"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("code", ["token_expired", "token_revoked"])
async def test_hard_response_owner_rejection_never_crosses_accounts(async_client, monkeypatch, path, code):
    account_ids = await _create_pool(async_client, refreshable=False)
    calls: list[str] = []

    async def owner(self, **kwargs):
        return account_ids[0]

    async def stream(payload, headers, access_token, account_id, **kwargs):
        calls.append(account_id)
        if code == "token_expired":
            raise ProxyResponseError(401, {"error": {"code": code, "message": "Synthetic access rejection"}})
        yield _revocation()

    monkeypatch.setattr(proxy_module.ProxyService, "_resolve_websocket_previous_response_owner", owner)
    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post(
        path,
        json={
            "model": "gpt-5.4",
            "instructions": "continue",
            "input": [],
            "stream": True,
            "previous_response_id": "resp_owned",
        },
    )
    assert response.status_code == 200
    assert '"response.failed"' in response.text
    assert calls == ["rejection-a"]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_refresh_only_warning_keeps_the_stored_access_token(async_client, monkeypatch, path):
    account_ids = await _create_pool(async_client, refreshable=True)
    async with SessionLocal() as session:
        repo = AccountsRepository(session)
        for account_id in account_ids:
            await repo.update_status(
                account_id, AccountStatus.REAUTH_REQUIRED, PERMANENT_FAILURE_CODES["refresh_token_invalidated"]
            )
    get_account_selection_cache().invalidate()
    calls = []

    async def must_not_refresh(*args, **kwargs):
        raise AssertionError("A refresh-only warning must not force token exchange")

    async def stream(payload, headers, access_token, account_id, **kwargs):
        calls.append(account_id)
        yield _completion()

    monkeypatch.setattr(AuthManager, "_refresh_tokens", must_not_refresh)
    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post(
        path, json={"model": "gpt-5.4", "instructions": "hi", "input": [], "stream": True}
    )
    assert response.status_code == 200
    assert '"resp_healthy"' in response.text
    assert len(calls) == 1
