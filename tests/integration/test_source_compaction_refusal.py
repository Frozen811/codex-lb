"""Source-owned compaction fails before native admission or accounting."""

from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.core.openai.model_registry import get_model_registry
from app.db.models import ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from tests.integration.model_source_helpers import _create_model_source, _enable_api_key_auth

pytestmark = pytest.mark.integration

_PATHS = [
    "/backend-api/codex/responses",
    "/backend-api/codex/responses/compact",
    "/v1/responses/compact",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _PATHS)
@pytest.mark.parametrize("trailing_slash", [False, True])
@pytest.mark.parametrize("enabled", [False, True])
async def test_source_compaction_refuses_before_admission_and_accounting(
    async_client, monkeypatch, path: str, trailing_slash: bool, enabled: bool
) -> None:
    model = "external-compact-refusal"
    source_id = await _create_model_source(
        async_client,
        name="compact-refusal",
        model=model,
        base_url="https://compact-refusal.example.invalid/v1",
        supports_responses=True,
    )
    if not enabled:
        disabled = await async_client.patch(f"/api/model-sources/{source_id}", json={"isEnabled": False})
        assert disabled.status_code == 200, disabled.text

    async def forbidden(*args, **kwargs):
        pytest.fail("source compaction must refuse before admission, reservation or dispatch")

    monkeypatch.setattr(proxy_api, "_opportunistic_admission_denial", forbidden)
    monkeypatch.setattr(proxy_api, "_enforce_request_limits", forbidden)
    monkeypatch.setattr(proxy_api, "_stream_responses", forbidden)
    monkeypatch.setattr(proxy_api, "stream_source_responses", forbidden)
    monkeypatch.setattr(proxy_service.ProxyService, "_select_account_with_budget", forbidden)
    body = {
        "model": model,
        "instructions": "compact this history",
        "input": [{"role": "user", "content": "compact history"}],
    }
    if not path.endswith("/compact"):
        body["input"].append({"type": "compaction_trigger"})
        body["stream"] = True
    response = await async_client.post(path + ("/" if trailing_slash else ""), json=body, follow_redirects=True)

    assert response.status_code == (400 if enabled else 503), response.text
    if path.endswith("/compact"):
        assert not response.history
    error = response.json()["error"]
    assert error["code"] == ("compaction_unsupported" if enabled else "model_source_disabled")
    assert error["type"] == ("invalid_request_error" if enabled else "upstream_error")
    async with SessionLocal() as session:
        assert await session.scalar(select(func.count()).select_from(ApiKeyUsageReservation)) == 0
        assert await session.scalar(select(func.count()).select_from(RequestLog)) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _PATHS)
async def test_assigned_source_compaction_preserves_key_limits(async_client, monkeypatch, path: str) -> None:
    model = "assigned-compact-refusal"
    source_id = await _create_model_source(
        async_client,
        name="assigned-compact",
        model=model,
        base_url="https://assigned-compact.example.invalid/v1",
        supports_responses=True,
    )
    await _enable_api_key_auth(async_client)
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "compact-refusal-key",
            "allowedModels": [model],
            "assignedSourceIds": [source_id],
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 10}],
        },
    )
    assert created.status_code == 200, created.text

    async def forbidden(*args, **kwargs):
        pytest.fail("an unsupported compact must not spend an assigned key's reservation")

    monkeypatch.setattr(proxy_api, "_enforce_request_limits", forbidden)
    body = {
        "model": model,
        "instructions": "compact this history",
        "input": [{"role": "user", "content": "compact history"}],
    }
    if not path.endswith("/compact"):
        body["input"].append({"type": "compaction_trigger"})
        body["stream"] = True
    response = await async_client.post(path, json=body, headers={"Authorization": f"Bearer {created.json()['key']}"})
    assert response.status_code == 400, response.text
    assert response.json()["error"]["code"] == "compaction_unsupported"
    async with SessionLocal() as session:
        assert await session.scalar(select(func.count()).select_from(ApiKeyUsageReservation)) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("path", _PATHS[1:])
@pytest.mark.parametrize("enabled", [False, True])
async def test_subscription_compact_precedence_survives_a_shadow_source(async_client, path: str, enabled: bool) -> None:
    registry = get_model_registry()
    models = registry.get_models_with_fallback()
    model = next(iter(models))
    source_id = await _create_model_source(
        async_client,
        name="shadow-native-compact",
        model=model,
        base_url="https://shadow-native.example.invalid/v1",
        supports_responses=True,
    )
    if not enabled:
        disabled = await async_client.patch(f"/api/model-sources/{source_id}", json={"isEnabled": False})
        assert disabled.status_code == 200
    response = await async_client.post(path, json={"model": model, "instructions": "compact", "input": []})
    assert response.status_code == 503, response.text
    assert response.json()["error"]["code"] == "no_accounts"
