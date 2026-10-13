from __future__ import annotations

import json
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

from app.db.models import Account, ModelSourceModel, RequestLog
from app.db.session import SessionLocal
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from app.modules.proxy.file_pin_repository import FileAccountPinRepository
from tests.integration.model_source_helpers import _create_model_source
from tests.integration.test_proxy_responses import _make_auth_json

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("condition", ["enabled", "disabled", "unavailable"])
@pytest.mark.parametrize("ownership", ["response", "file"])
async def test_native_owners_precede_competing_sources(async_client, monkeypatch, path, condition, ownership):
    auth = _make_auth_json("native-owner", "source-owner@example.invalid")
    imported = await async_client.post(
        "/api/accounts/import", files={"auth_json": ("auth.json", json.dumps(auth), "application/json")}
    )
    assert imported.status_code == 200, imported.text
    model = "external-owned-history"
    source_id = await _create_model_source(
        async_client,
        name="competing-source",
        model=model,
        base_url="https://must-not-dispatch.invalid/v1",
        supports_responses=True,
    )
    async with SessionLocal() as session:
        owner = (await session.execute(select(Account))).scalars().one()
        if ownership == "response":
            session.add(
                RequestLog(
                    account_id=owner.id,
                    request_id="resp_native",
                    model=model,
                    status="success",
                    input_tokens=1,
                    output_tokens=1,
                )
            )
        else:
            await FileAccountPinRepository(session).claim("file-native", owner.id, ttl_seconds=3600)
        if condition == "unavailable":
            row = (
                (await session.execute(select(ModelSourceModel).where(ModelSourceModel.source_id == source_id)))
                .scalars()
                .one()
            )
            row.is_available = False
        await session.commit()
        session.expunge_all()
    if condition == "disabled":
        assert (
            await async_client.patch(f"/api/model-sources/{source_id}", json={"isEnabled": False})
        ).status_code == 200

    seen = []

    async def select_owner(self, deadline, **kwargs):
        seen.append(kwargs.get("preferred_account_id"))
        return proxy_service.AccountSelection(account=owner, error_message=None)

    async def stream(payload, headers, access_token, account_id, **kwargs):
        assert account_id == "native-owner"
        event = {
            "type": "response.completed",
            "response": {
                "id": "resp_native_next",
                "object": "response",
                "status": "completed",
                "output": [],
                "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
            },
        }
        yield f"data: {json.dumps(event)}\n\n"

    async def no_source(*args, **kwargs):
        pytest.fail("native continuity must not dispatch to an external source")

    monkeypatch.setattr(proxy_service.ProxyService, "_select_account_with_budget", select_owner)
    monkeypatch.setattr(proxy_service.ProxyService, "_ensure_fresh_with_budget", AsyncMock(return_value=owner))
    monkeypatch.setattr(proxy_service, "core_stream_responses", stream)
    monkeypatch.setattr(proxy_api, "_source_responses_response", no_source)
    body = {"model": model, "input": "continue", "stream": True}
    if ownership == "response":
        body["previous_response_id"] = "resp_native"
    else:
        body["input"] = [{"role": "user", "content": [{"type": "input_file", "file_id": "file-native"}]}]
    response = await async_client.post(path, json=body)
    assert response.status_code == 200, response.text
    assert "resp_native_next" in response.text
    assert seen and all(account_id == owner.id for account_id in seen)
