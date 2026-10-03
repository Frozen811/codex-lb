from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from app.core import shutdown as shutdown_state
from app.core.config.settings import get_settings
from app.main import create_app

pytestmark = pytest.mark.integration


@pytest.fixture(autouse=True)
def _database_schema(db_setup):
    del db_setup


@pytest.mark.parametrize(
    "method,path",
    [("POST", "/internal/drain/start"), ("POST", "/internal/drain/stop"), ("GET", "/internal/drain/status")],
)
@pytest.mark.parametrize(
    "peer,headers",
    [
        ("203.0.113.10", {"X-Forwarded-For": "127.0.0.1"}),
        ("127.0.0.1", {"X-Forwarded-For": "203.0.113.10"}),
        ("127.0.0.1", {"X-Forwarded-For": "127.0.0.1", "CF-Connecting-IP": "203.0.113.10"}),
    ],
)
@pytest.mark.asyncio
async def test_drain_routes_reject_projected_locality_without_direct_local_provenance(
    monkeypatch,
    method,
    path,
    peer,
    headers,
):
    monkeypatch.setenv("FORWARDED_ALLOW_IPS", "*")
    get_settings.cache_clear()
    shutdown_state.reset()
    before = (
        shutdown_state.is_draining(),
        shutdown_state.is_shutdown_committed(),
        shutdown_state.remaining_drain_timeout_seconds(),
    )
    async with AsyncClient(
        transport=ASGITransport(app=create_app(), client=(peer, 12345)), base_url="http://127.0.0.1:2455"
    ) as client:
        response = await client.request(method, path, headers=headers)
    assert response.status_code == 403, response.text
    assert (
        shutdown_state.is_draining(),
        shutdown_state.is_shutdown_committed(),
        shutdown_state.remaining_drain_timeout_seconds(),
    ) == before


@pytest.mark.asyncio
async def test_direct_loopback_drain_works_with_projection_and_firewall_trust_enabled(monkeypatch):
    monkeypatch.setenv("FORWARDED_ALLOW_IPS", "127.0.0.1")
    monkeypatch.setenv("CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS", "true")
    get_settings.cache_clear()
    shutdown_state.reset()
    async with AsyncClient(
        transport=ASGITransport(app=create_app(), client=("127.0.0.1", 12345)), base_url="http://127.0.0.1:2455"
    ) as client:
        try:
            response = await client.post("/internal/drain/start")
            assert response.status_code == 200
            assert shutdown_state.is_draining()
            status = await client.get("/internal/drain/status")
            assert status.status_code == 200
            assert status.json()["checks"]["draining"] == "true"
            stopped = await client.post("/internal/drain/stop")
            assert stopped.status_code == 200
            assert not shutdown_state.is_draining()
        finally:
            shutdown_state.reset()
