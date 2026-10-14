from __future__ import annotations

from http.cookies import SimpleCookie

import pytest
from httpx import ASGITransport, AsyncClient
from starlette.types import Receive, Scope, Send

from app.core.socket_peer import _capture_raw_socket_peer
from app.modules.dashboard_auth import service as auth_service

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("hours", [876000, 8760000])
@pytest.mark.parametrize("peer", ["127.0.0.1", "192.0.2.50"])
async def test_discussion_1820_long_lifetime_roundtrip_and_absolute_cookie_policy(
    async_client, app_instance, monkeypatch: pytest.MonkeyPatch, hours: int, peer: str
) -> None:
    clock = [1_800_000_000]
    monkeypatch.setattr(auth_service, "time", lambda: clock[0])
    password = "synthetic-session-password"
    setup = await async_client.post("/api/dashboard-auth/password/setup", json={"password": password})
    assert setup.status_code == 200, setup.text
    configured = hours * 3600
    update = await async_client.put("/api/settings", json={"dashboardSessionTtlSeconds": configured})
    assert update.status_code == 200, update.text
    assert update.json()["dashboardSessionTtlSeconds"] == configured

    async def app_with_socket_peer(scope: Scope, receive: Receive, send: Send) -> None:
        _capture_raw_socket_peer(scope)
        await app_instance(scope, receive, send)

    transport = ASGITransport(app=app_with_socket_peer, client=(peer, 41000))
    async with AsyncClient(transport=transport, base_url="http://localhost") as browser:
        login = await browser.post("/api/dashboard-auth/password/login", json={"password": password})
        assert login.status_code == 200, login.text
        cookies = SimpleCookie()
        cookies.load(login.headers["set-cookie"])
        cookie = cookies[auth_service.DASHBOARD_SESSION_COOKIE]
        expected = configured if peer == "127.0.0.1" else 43200
        assert int(cookie["max-age"]) == expected
        session = auth_service.get_dashboard_session_store().get(cookie.value)
        assert session is not None
        assert session.expires_at - session.issued_at == expected

        read = await browser.get("/api/settings")
        assert read.status_code == 200, read.text
        assert read.json()["dashboardSessionTtlSeconds"] == configured
        changed = await browser.put("/api/settings", json={"dashboardSessionTtlSeconds": 3600})
        assert changed.status_code == 200, changed.text
        clock[0] = session.expires_at - 1
        reused = await browser.get("/api/settings")
        assert reused.status_code == 200, reused.text
        assert "set-cookie" not in reused.headers
        clock[0] = session.expires_at + 1
        expired = await browser.get("/api/settings")
        assert expired.status_code == 401
        assert expired.json()["error"]["code"] == "authentication_required"
