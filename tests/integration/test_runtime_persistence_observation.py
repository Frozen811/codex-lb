from __future__ import annotations

import asyncio
import json

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import select

from app.core import shutdown as shutdown_state
from app.db.models import ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.api_keys.service import ApiKeysService
from app.modules.proxy import service as proxy_service
from tests.integration.test_detached_persistence import raw_client as raw_client  # noqa: F401
from tests.integration.test_proxy_api_extended import _import_account

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "path", ["/backend-api/codex/responses", "/backend-api/codex/responses/", "/v1/responses", "/v1/responses/"]
)
async def test_drain_status_observes_real_http_reservation_after_response_close(raw_client, monkeypatch, path):
    client, app = raw_client
    await _import_account(client, "observed-settlement", "observation@example.com")
    settings = await client.put(
        "/api/settings", json={"apiKeyAuthEnabled": True, "httpDownstreamTransportPolicy": "always_http"}
    )
    assert settings.status_code == 200, settings.text
    key = await client.post(
        "/api/api-keys/",
        json={
            "name": "owned-settlement",
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 20000}],
        },
    )
    assert key.status_code == 200, key.text
    service = get_proxy_service_for_app(app)
    entered = asyncio.Event()
    release = asyncio.Event()
    settle = ApiKeysService.finalize_usage_reservation

    async def held_settlement(self, *args, **kwargs):
        entered.set()
        await release.wait()
        return await settle(self, *args, **kwargs)

    async def upstream(*args, **kwargs):
        yield 'data: {"type":"response.created","response":{"id":"resp_observation","status":"in_progress"}}\n\n'
        yield (
            "data: "
            + json.dumps(
                {
                    "type": "response.completed",
                    "response": {
                        "id": "resp_observation",
                        "status": "completed",
                        "output": [],
                        "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
                    },
                }
            )
            + "\n\n"
        )

    monkeypatch.setattr(ApiKeysService, "finalize_usage_reservation", held_settlement)
    monkeypatch.setattr(proxy_service, "core_stream_responses", upstream)
    try:
        response = await client.post(
            path,
            headers={"Authorization": f"Bearer {key.json()['key']}", "user-agent": "codex-cli/0.154.0"},
            json={"model": "gpt-5.1", "instructions": "", "input": "hi", "stream": True},
        )
        assert response.status_code == 200 and "response.completed" in response.text, response.text
        await asyncio.wait_for(entered.wait(), timeout=2)
        async with SessionLocal() as database:
            reservation = (await database.scalars(select(ApiKeyUsageReservation))).one()
            assert reservation.status == "reserved"
        shutdown_state.begin_drain(30)
        async with AsyncClient(
            transport=ASGITransport(app=app, client=("127.0.0.1", 12345)), base_url="http://127.0.0.1"
        ) as observer:
            pending = (await observer.get("/internal/drain/status")).json()["checks"]
            assert pending["in_flight"] == "0"
            assert pending["request_persistence_state"] == "pending"
            assert int(pending["api_key_settlements_pending"]) >= 1
            release.set()
            assert await service.drain_persistence_tasks(timeout_seconds=5)
            drained = (await observer.get("/internal/drain/status")).json()["checks"]
            assert drained["request_persistence_state"] == "drained"
            assert drained["request_persistence_pending"] == "0"
        async with SessionLocal() as database:
            reservation = (await database.scalars(select(ApiKeyUsageReservation))).one()
            assert reservation.status == "finalized"
            log = (await database.scalars(select(RequestLog))).one()
            assert log.status == "success" and log.input_tokens == 1 and log.output_tokens == 2
    finally:
        release.set()
        shutdown_state.reset()
        await service.drain_persistence_tasks(timeout_seconds=5)
