from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from aiohttp import web
from sqlalchemy import select

from app.db.models import Account, ModelSource
from app.db.session import SessionLocal
from app.modules.usage.updater import UsageUpdater
from tests.integration.model_source_helpers import _create_model_source, _enable_api_key_auth, stub_source_upstreams

pytestmark = pytest.mark.integration


async def _import(async_client, *, email: str, workspace: str, token: str = "synthetic-access") -> str:
    response = await async_client.post(
        "/api/accounts/import",
        files={
            "auth_json": (
                "auth.json",
                json.dumps(
                    {
                        "email": email,
                        "plan_type": "team",
                        "workspace_id": workspace,
                        "workspace_label": f"Business {workspace}",
                        "seat_type": "standard",
                        "tokens": {"access_token": token, "account_id": workspace},
                    }
                ),
                "application/json",
            )
        },
    )
    assert response.status_code == 200, response.text
    return response.json()["accountId"]


@pytest.mark.asyncio
async def test_access_only_export_round_trip_preserves_identity_and_siblings(async_client, monkeypatch):
    monkeypatch.setattr(UsageUpdater, "refresh_accounts", AsyncMock())
    slots = {}
    for workspace, email in [("a", "a1@example.invalid"), ("a", "a2@example.invalid"), ("b", "b1@example.invalid")]:
        slots[email] = await _import(async_client, email=email, workspace=workspace, token=f"token-{email}")
    assert len(set(slots.values())) == 3
    for email, account_id in slots.items():
        exported = await async_client.post(f"/api/accounts/{account_id}/export/auth")
        assert exported.status_code == 200, exported.text
        auth = exported.json()["codexAuthJson"]
        assert auth.get("email") == email
        assert auth.get("plan_type") == "team"
        assert auth.get("workspace_id") == email[0]
        assert auth.get("workspace_label") == f"Business {email[0]}"
        assert auth.get("seat_type") == "standard"
        assert auth["tokens"]["id_token"] is None
        assert auth["tokens"]["refresh_token"] is None
        restored = await async_client.post(
            "/api/accounts/import", files={"auth_json": ("auth.json", json.dumps(auth), "application/json")}
        )
        assert restored.status_code == 200, restored.text
        assert restored.json()["accountId"] == account_id
    async with SessionLocal() as session:
        accounts = list((await session.execute(select(Account))).scalars())
        assert len(accounts) == 3
        for account in accounts:
            assert account.id == slots[account.email]
            assert account.workspace_id == account.email[0]
            assert account.status.value == "active"


@pytest.mark.asyncio
async def test_business_reimport_updates_only_selected_credential_slot(async_client, monkeypatch):
    monkeypatch.setattr(UsageUpdater, "refresh_accounts", AsyncMock())
    first = await _import(async_client, email="first@example.invalid", workspace="shared", token="first-token")
    sibling = await _import(async_client, email="sibling@example.invalid", workspace="shared", token="sibling-token")
    foreign = await _import(async_client, email="first@example.invalid", workspace="other", token="other-token")
    async with SessionLocal() as session:
        sibling_account = await session.get(Account, sibling)
        foreign_account = await session.get(Account, foreign)
        assert sibling_account is not None and foreign_account is not None
        sibling_before = sibling_account.access_token_encrypted
        foreign_before = foreign_account.access_token_encrypted
    assert (
        await _import(async_client, email="first@example.invalid", workspace="shared", token="rotated-token") == first
    )
    async with SessionLocal() as session:
        sibling_account = await session.get(Account, sibling)
        foreign_account = await session.get(Account, foreign)
        assert sibling_account is not None and foreign_account is not None
        assert sibling_account.access_token_encrypted == sibling_before
        assert foreign_account.access_token_encrypted == foreign_before


@pytest.mark.asyncio
async def test_api_key_source_headless_auth_is_encrypted_and_dispatches_without_subscription(async_client):
    await _enable_api_key_auth(async_client)
    calls = []

    async def upstream(request: web.Request) -> web.Response:
        calls.append((request.path, request.headers.get("Authorization")))
        return web.json_response(
            {
                "id": "resp_api_auth",
                "object": "response",
                "status": "completed",
                "model": "api-auth-model",
                "output": [],
                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            }
        )

    async with stub_source_upstreams() as start:
        source_id = await _create_model_source(
            async_client,
            name="api-auth",
            model="api-auth-model",
            base_url=await start(upstream),
            supports_responses=True,
        )
        listed = await async_client.get("/api/model-sources/")
        assert "token-api-auth" not in listed.text
        created_key = await async_client.post("/api/api-keys", json={"name": "api-auth-relay"})
        assert created_key.status_code == 200, created_key.text
        key = created_key.json()["key"]
        response = await async_client.post(
            "/v1/responses",
            headers={"Authorization": f"Bearer {key}"},
            json={"model": "api-auth-model", "input": "Synthetic test", "stream": False},
        )
        assert response.status_code == 200, response.text
        assert response.json()["id"] == "resp_api_auth"
        assert calls == [("/v1/responses", "Bearer token-api-auth")]
        async with SessionLocal() as session:
            source = await session.get(ModelSource, source_id)
            assert source is not None and source.api_key_encrypted is not None
            assert b"token-api-auth" not in source.api_key_encrypted
            assert not list((await session.execute(select(Account))).scalars())
