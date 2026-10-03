from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.requests import Request

from app.core.audit.service import drain_audit_log_tasks
from app.core.auth.dashboard_mode import _get_trusted_header_auth
from app.core.config.settings import get_settings
from app.main import create_app

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    ("peer", "forwarded", "identity_headers", "expected"),
    [
        ("127.0.0.1", "203.0.113.42", [("Remote-User", "setup@example.invalid")], 200),
        ("203.0.113.42", "127.0.0.1", [("Remote-User", "spoof@example.invalid")], 401),
        (
            "127.0.0.1",
            "203.0.113.42",
            [("Remote-User", "setup@example.invalid"), ("remote-user", "setup@example.invalid")],
            401,
        ),
    ],
)
@pytest.mark.asyncio
async def test_trusted_header_route_uses_socket_proxy_not_projected_user(
    monkeypatch,
    _reset_db_state,
    peer,
    forwarded,
    identity_headers,
    expected,
):
    monkeypatch.setenv("CODEX_LB_DASHBOARD_AUTH_MODE", "trusted_header")
    monkeypatch.setenv("CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("CODEX_LB_FIREWALL_TRUSTED_PROXY_CIDRS", "127.0.0.1/32")
    # Projection is intentionally broader than identity authority to prove the
    # two settings cannot substitute for one another.
    monkeypatch.setenv("FORWARDED_ALLOW_IPS", "*")
    get_settings.cache_clear()
    app = create_app()
    transport = ASGITransport(app=app, client=(peer, 12345))
    async with AsyncClient(transport=transport, base_url="http://setup.example.test") as client:
        response = await client.get(
            "/api/settings",
            headers=[("X-Forwarded-For", forwarded), ("X-Forwarded-Proto", "https"), *identity_headers],
        )
        assert response.status_code == expected, response.text
        if expected == 401:
            assert response.json()["error"]["code"] == "proxy_auth_required"
        else:
            session = await client.get(
                "/api/dashboard-auth/session", headers=[("X-Forwarded-For", forwarded), *identity_headers]
            )
            assert session.status_code == 200
            assert session.json()["authenticated"] is True
            assert session.json()["authMode"] == "trusted_header"
            mutation = await client.put(
                "/api/settings",
                json={"prohibitFastMode": True},
                headers=[("X-Forwarded-For", forwarded), *identity_headers],
            )
            assert mutation.status_code == 200
            await drain_audit_log_tasks(timeout_seconds=5)
            audit = await client.get("/api/audit-logs", headers=[("X-Forwarded-For", forwarded), *identity_headers])
            assert audit.status_code == 200
            assert "setup@example.invalid" in audit.text
            assert forwarded in audit.text


def test_uncaptured_identity_request_fails_closed(monkeypatch):
    monkeypatch.setenv("CODEX_LB_DASHBOARD_AUTH_MODE", "trusted_header")
    monkeypatch.setenv("CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS", "true")
    monkeypatch.setenv("CODEX_LB_FIREWALL_TRUSTED_PROXY_CIDRS", "127.0.0.1/32")
    get_settings.cache_clear()
    request = Request(
        {
            "type": "http",
            "method": "GET",
            "path": "/api/settings",
            "scheme": "http",
            "headers": [(b"remote-user", b"uncaptured@example.invalid")],
            "client": ("127.0.0.1", 12345),
        }
    )
    assert _get_trusted_header_auth(request) is None
