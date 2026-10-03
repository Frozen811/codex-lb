from __future__ import annotations

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

import app.core.startup as startup_module
import app.main as main_module

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_missing_dashboard_has_actionable_source_and_package_recovery(tmp_path: Path, monkeypatch, db_setup):
    del db_setup
    monkeypatch.setattr(main_module, "__file__", str(tmp_path / "app" / "main.py"))
    monkeypatch.setattr(startup_module, "_bridge_durable_schema_ready", True)
    monkeypatch.setattr(startup_module, "_bridge_registration_complete", True)
    app = main_module.create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://127.0.0.1:2455") as client:
        ready = await client.get("/health/ready")
        assert ready.status_code == 200
        response = await client.get("/")
    assert response.status_code == 503
    message = response.json()["detail"]
    assert "pinned Bun" in message
    assert "bun install --frozen-lockfile" in message
    assert "bun --bun run build" in message
    assert "installed package/image" in message
    assert "complete fork artifact" in message
