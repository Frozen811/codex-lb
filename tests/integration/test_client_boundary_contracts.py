from __future__ import annotations

import json
import time
from contextlib import asynccontextmanager
from urllib.parse import parse_qs, urlparse

import aiohttp
import pytest
from fastapi.testclient import TestClient

from app.core.clients import oauth as oauth_client
from app.core.clients import proxy as proxy_client
from app.core.clients import proxy_websocket
from app.core.usage.models import UsagePayload
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.accounts.service import AccountsService
from app.modules.oauth import service as oauth_service
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from tests.integration import test_http_responses_bridge as bridge
from tests.integration.test_accounts_api_probe import _import_test_account
from tests.integration.test_proxy_images import _disable_http_bridge as _disable_http_bridge
from tests.integration.test_proxy_images import _make_auth_json, _sse

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("outcome", ["available", "rollover", "failed", "exhausted", "operator_race"])
async def test_weekly_only_prolite_probe_recovery(async_client, monkeypatch, outcome):
    account_id = await _import_test_account(
        async_client, email="weekly@example.invalid", account_id="weekly", plan_type="self_serve_business_prolite"
    )
    now = int(time.time())
    old_reset = now - 1 if outcome == "rollover" else now + 18 * 3600
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        account.status = AccountStatus.RATE_LIMITED
        account.blocked_at = now - 60
        account.reset_at = old_reset
        await session.commit()

    async def probe(self, **kwargs):
        assert kwargs["chatgpt_account_id"] == "weekly"
        assert kwargs["model"] == "gpt-6-astra"
        return 429 if outcome == "failed" else 200

    async def usage(**kwargs):
        if outcome == "operator_race":
            async with SessionLocal() as session:
                account = await session.get(Account, account_id)
                assert account is not None
                account.status = AccountStatus.PAUSED
                await session.commit()
        return UsagePayload.model_validate(
            {
                "plan_type": "self_serve_business_prolite",
                "rate_limit": {
                    "primary_window": {
                        "used_percent": 100 if outcome == "exhausted" else 1,
                        "reset_at": now + 7 * 86400,
                        "limit_window_seconds": 10080 * 60,
                    },
                    "secondary_window": {"used_percent": 0, "reset_at": None, "limit_window_seconds": 0},
                },
            }
        )

    monkeypatch.setattr(AccountsService, "_send_probe_request", probe)
    monkeypatch.setattr("app.modules.usage.updater.fetch_usage", usage)
    response = await async_client.post(f"/api/accounts/{account_id}/probe", json={"model": "gpt-6-astra"})
    assert response.status_code == 200, response.text
    expected = (
        "active" if outcome in ("available", "rollover") else "paused" if outcome == "operator_race" else "rate_limited"
    )
    assert response.json()["accountStatusAfter"] == expected, response.text
    async with SessionLocal() as session:
        account = await session.get(Account, account_id)
        assert account is not None
        assert account.status.value == expected
        assert account.plan_type == "prolite"
        if expected == "active":
            assert account.reset_at is None and account.blocked_at is None
    if expected == "active":
        calls = []

        async def stream(payload, headers, access_token, account_id, **kwargs):
            calls.append((payload.model, account_id))
            yield _sse(
                {"type": "response.completed", "response": {"id": "resp_weekly", "status": "completed", "output": []}}
            )

        async def fresh(self, account, **kwargs):
            return account

        monkeypatch.setattr(proxy_service, "core_stream_responses", stream)
        monkeypatch.setattr(proxy_service.ProxyService, "_ensure_fresh_with_budget", fresh)
        inference = await async_client.post("/v1/responses", json={"model": "gpt-6-astra", "input": [], "stream": True})
        assert inference.status_code == 200 and "response.completed" in inference.text, inference.text
        assert calls == [("gpt-6-astra", "weekly")]


@pytest.fixture
def failed_oauth_transport(monkeypatch):
    class Session:
        def post(self, *args, **kwargs):
            raise aiohttp.ClientConnectionError("https://private.invalid?code=private&verifier=secret")

    @asynccontextmanager
    async def lease(session):
        yield Session()

    async def direct(*args):
        return None

    monkeypatch.setattr(oauth_client, "lease_http_session", lease)
    monkeypatch.setattr(oauth_service, "_oauth_route", direct)


async def test_device_start_returns_safe_transport_error(async_client, failed_oauth_transport, caplog):
    response = await async_client.post("/api/oauth/start", json={"forceMethod": "device"})
    assert response.status_code == 502, response.text
    assert response.json()["error"]["code"] == "transport_error"
    assert "Unable to connect to the OAuth server" in response.text
    assert "private.invalid" not in response.text + caplog.text
    assert "verifier=secret" not in response.text + caplog.text


@pytest.mark.parametrize("method", ["browser", "manual"])
async def test_callback_network_error_is_terminal_and_safe(
    async_client, failed_oauth_transport, monkeypatch, unused_tcp_port, method, caplog
):
    monkeypatch.setattr(oauth_service, "OAUTH_CALLBACK_PORT", unused_tcp_port)
    started = await async_client.post("/api/oauth/start", json={"forceMethod": "browser"})
    assert started.status_code == 200, started.text
    body = started.json()
    state = parse_qs(urlparse(body["authorizationUrl"]).query)["state"][0]
    callback = f"http://127.0.0.1:{unused_tcp_port}/auth/callback?code=synthetic-code&state={state}"
    if method == "browser":
        async with aiohttp.ClientSession() as client:
            async with client.get(callback) as response:
                assert response.status == 200
                text = await response.text()
    else:
        response = await async_client.post(
            "/api/oauth/manual-callback", json={"callbackUrl": callback, "flowId": body["flowId"]}
        )
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "error"
        text = response.text
    assert "Unable to connect to the OAuth server" in text
    status = await async_client.get("/api/oauth/status", params={"flowId": body["flowId"]})
    assert status.json()["status"] == "error", status.text
    assert "Unable to connect to the OAuth server" in status.json()["errorMessage"]
    assert "private.invalid" not in text + caplog.text
    assert "synthetic-code" not in caplog.text


IDENTITIES = ["ccodex-internal", "ccodex-handoff-worker", "ccodex-internal-evil"]


def fingerprint(identity):
    return {"originator": identity, "user-agent": f"{identity}/0.159.3", "version": "0.159.3"}


def assert_fingerprint(headers, identity, builder):
    built = {key.lower(): value for key, value in builder(headers, "synthetic", "synthetic-account").items()}
    if identity in IDENTITIES[:2]:
        assert all(built[key] == value for key, value in fingerprint(identity).items())
    else:
        assert built["user-agent"].startswith("codex_cli_rs/")
        assert not proxy_client._is_native_codex_request(headers)


@pytest.mark.parametrize("identity", IDENTITIES)
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
async def test_ccodex_http_identity_and_transport_policy(async_client, monkeypatch, identity, path):
    await _import_test_account(async_client, email="identity@example.invalid", account_id="identity")
    calls = []

    async def stream(payload, headers, *args, **kwargs):
        calls.append(dict(headers))
        assert_fingerprint(headers, identity, proxy_client._build_upstream_headers)
        yield _sse(
            {"type": "response.completed", "response": {"id": "resp_identity", "status": "completed", "output": []}}
        )

    async def fresh(self, account, **kwargs):
        return account

    monkeypatch.setattr(proxy_service, "core_stream_responses", stream)
    monkeypatch.setattr(proxy_service.ProxyService, "_ensure_fresh_with_budget", fresh)
    response = await async_client.post(
        path, json={"model": "gpt-6-astra", "input": [], "stream": True}, headers=fingerprint(identity)
    )
    assert response.status_code == 200 and "response.completed" in response.text, response.text
    assert len(calls) == 1


@pytest.mark.parametrize("identity", IDENTITIES)
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
def test_ccodex_native_websocket_identity(app_instance, monkeypatch, identity, path):
    calls = []

    async def authorize(_authorization, *, request=None):
        return None

    async def fresh(self, account, **kwargs):
        return account

    async def connect(headers, *args, **kwargs):
        calls.append(dict(headers))
        assert_fingerprint(headers, identity, proxy_websocket._build_upstream_websocket_headers)
        return bridge._FakeBridgeUpstreamWebSocket("resp_identity")

    monkeypatch.setattr(proxy_api, "validate_proxy_api_key_authorization", authorize)
    monkeypatch.setattr(proxy_service.ProxyService, "_ensure_fresh_with_budget", fresh)
    monkeypatch.setattr(proxy_service, "connect_responses_websocket", connect)
    with TestClient(app_instance, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        imported = client.post(
            "/api/accounts/import",
            files={"auth_json": ("auth.json", json.dumps(_make_auth_json("identity", "identity@example.invalid")))},
        )
        assert imported.status_code == 200, imported.text
        with client.websocket_connect(path, headers=fingerprint(identity)) as ws:
            ws.send_json({"type": "response.create", "model": "gpt-6-astra", "input": [], "stream": True})
            for _ in range(10):
                if ws.receive_json()["type"] == "response.completed":
                    break
            else:
                pytest.fail("Missing terminal")
    assert len(calls) == 1
