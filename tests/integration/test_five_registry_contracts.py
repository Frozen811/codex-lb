from __future__ import annotations

import json
from datetime import timezone
from http.cookies import SimpleCookie
from types import SimpleNamespace

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from httpx import ASGITransport, AsyncClient

from app.core.clients import proxy as core_proxy
from app.core.openai.requests import ResponsesCompactRequest, ResponsesRequest
from app.core.utils.time import utcnow
from app.db.models import Account, AccountStatus
from app.db.session import SessionLocal
from app.modules.dashboard_auth import service as auth_service
from app.modules.proxy import service as proxy_service
from app.modules.proxy._load_balancer.tunables import RoutingTunables
from app.modules.proxy._load_balancer.types import RuntimeState
from app.modules.proxy.affinity import _codex_session_selection_key
from app.modules.proxy.load_balancer import LoadBalancer, _state_from_account
from tests.integration.test_load_balancer_integration import _repo_factory
from tests.integration.test_plan_json_contracts import _import_plan
from tests.unit.test_routing_tunables import _account, _usage

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("configured", [3600, 1224000, 2592000, 2592001, 31536000])
async def test_remote_admin_cookie_honors_configured_absolute_lifetime(
    async_client, app_instance, monkeypatch, configured
):
    clock = [1_800_000_000]
    monkeypatch.setattr(auth_service, "time", lambda: clock[0])
    setup = await async_client.post("/api/dashboard-auth/password/setup", json={"password": "synthetic-password"})
    assert setup.status_code == 200
    settings = await async_client.put("/api/settings", json={"dashboardSessionTtlSeconds": configured})
    assert settings.status_code == 200, settings.text
    expected = configured if configured <= 2592000 else 43200
    transport = ASGITransport(app=app_instance, client=("203.0.113.21", 41000))
    async with AsyncClient(transport=transport, base_url="http://lb.example") as remote:
        login = await remote.post("/api/dashboard-auth/password/login", json={"password": "synthetic-password"})
        assert login.status_code == 200, login.text
        cookie = SimpleCookie()
        cookie.load(login.headers["set-cookie"])
        session_cookie = next(iter(cookie.values()))
        assert int(session_cookie["max-age"]) == expected
        state = auth_service.get_dashboard_session_store().get(session_cookie.value)
        assert state is not None and state.expires_at - state.issued_at == expected
        for elapsed in sorted({min(43201, expected - 1), expected - 1}):
            clock[0] = state.issued_at + elapsed
            reused = await remote.get("/api/settings")
            assert reused.status_code == 200
            assert "set-cookie" not in reused.headers
        clock[0] = state.expires_at + 1
        expired = await remote.get("/api/settings")
        assert expired.status_code == 401
        assert expired.json()["error"]["code"] == "authentication_required"


@pytest.mark.parametrize("plan", ["plus", "pro", "future-plan"])
@pytest.mark.parametrize("used, expected", [(38.0, 39.0), (98.9, 99.0), (99.0, 99.0), (99.5, 99.5), (100.0, 100.0)])
def test_lease_pressure_has_plan_independent_units_and_retains_exhaustion(plan, used, expected):
    now = utcnow().replace(tzinfo=timezone.utc).timestamp()
    account = _account("lease-unit-owner")
    account.plan_type = plan
    entry = _usage(account.id, used, now)
    state = _state_from_account(
        account=account,
        primary_entry=entry,
        secondary_entry=None,
        runtime=RuntimeState(leased_tokens=10240),
        now=now,
        routing_tunables=RoutingTunables(inflight_penalty_pct=0, lease_token_weight=1),
        soft_drain_enabled=False,
    )
    assert state.used_percent == pytest.approx(expected)
    assert entry.used_percent == used
    assert account.status == AccountStatus.ACTIVE


@pytest.mark.asyncio
@pytest.mark.parametrize("sticky", [False, True])
async def test_open_leases_preserve_real_db_relative_availability_and_sticky_budget(db_setup, sticky):
    from app.db.models import StickySessionKind
    from app.modules.accounts.repository import AccountsRepository
    from app.modules.proxy.sticky_repository import StickySessionsRepository
    from app.modules.usage.repository import UsageRepository

    now = utcnow().replace(tzinfo=timezone.utc).timestamp()
    sticky_key = _codex_session_selection_key("lease-thread")
    async with SessionLocal() as database:
        for account_id, used in [("a-heavy", 95.0), ("z-light", 38.0)]:
            await AccountsRepository(database).upsert(_account(account_id))
            primary = _usage(account_id, 10.0, now)
            for window, percent in [("primary", 10.0), ("secondary", used)]:
                await UsageRepository(database).add_entry(
                    account_id=account_id,
                    used_percent=percent,
                    window=window,
                    reset_at=int(now + (3600 if window == "primary" else 604800)),
                    window_minutes=300 if window == "primary" else 10080,
                    recorded_at=primary.recorded_at,
                )
        if sticky:
            await StickySessionsRepository(database).upsert(sticky_key, "a-heavy", kind=StickySessionKind.CODEX_SESSION)
    balancer = LoadBalancer(_repo_factory)
    leases = []
    try:
        for account_id in ("a-heavy", "z-light"):
            lease = await balancer.acquire_account_lease(account_id, kind="stream", estimated_tokens=10240)
            assert lease is not None
            leases.append(lease)
        row = SimpleNamespace(soft_drain_enabled=False)
        result = await balancer.select_account(
            sticky_key if sticky else None,
            sticky_kind=StickySessionKind.CODEX_SESSION,
            routing_strategy="relative_availability",
            relative_availability_top_k=1,
            sticky_source="session_header" if sticky else None,
            legacy_sticky_key="lease-thread" if sticky else None,
            secondary_budget_threshold_pct=95.0,
            dashboard_settings=row,
        )
        assert result.account is not None and result.account.id == "z-light"
        async with SessionLocal() as database:
            for account_id in ("a-heavy", "z-light"):
                stored = await database.get(Account, account_id)
                assert stored is not None and stored.status == AccountStatus.ACTIVE
            if sticky:
                saved = await StickySessionsRepository(database).get_entry(
                    sticky_key, kind=StickySessionKind.CODEX_SESSION
                )
                assert saved is not None and saved.account_id == "z-light"
    finally:
        for lease in leases:
            await balancer.release_account_lease(lease)


@pytest.mark.parametrize("request_type", [ResponsesRequest, ResponsesCompactRequest])
@pytest.mark.parametrize("instructions", [None, "", "top-level context"])
def test_developer_message_is_durable_input_even_without_instructions(request_type, instructions):
    developer = {"type": "message", "role": "developer", "content": [{"type": "input_text", "text": "key-17=34620"}]}
    payload = {"model": "gpt-5.2", "input": [developer, {"role": "user", "content": "Read key-17"}]}
    if instructions is not None:
        payload["instructions"] = instructions
    request = request_type.model_validate(payload)
    assert request.input == payload["input"]
    assert request.to_payload()["input"] == payload["input"]
    assert request.instructions == (instructions or "")


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("prewarm", [False, True])
async def test_developer_context_survives_actual_http_previous_response_chain(async_client, monkeypatch, path, prewarm):
    await _import_plan(async_client, "plus")
    history = {}
    observed = []
    developer = {"role": "developer", "content": [{"type": "input_text", "text": "key-17=34620; Привет\r\n"}]}

    async def upstream(request):
        wire = await request.json()
        observed.append(wire)
        response_id = f"resp_chain_{len(observed)}"
        inherited = history.get(wire.get("previous_response_id"), [])
        history[response_id] = [*inherited, *wire["input"]]
        answer = "34620" if developer in history[response_id] else "missing reference"
        frames = [
            {
                "type": "response.completed",
                "response": {
                    "id": response_id,
                    "status": "completed",
                    "model": "gpt-5.2",
                    "output": [
                        {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": answer}]}
                    ],
                    "usage": {"input_tokens": 20, "output_tokens": 2},
                },
            }
        ]
        return web.Response(
            text="".join(f"data: {json.dumps(frame)}\n\n" for frame in frames), content_type="text/event-stream"
        )

    application = web.Application()
    application.router.add_post("/codex/responses", upstream)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(application) as server, aiohttp.ClientSession() as session:

        async def stream_local(payload, headers, access_token, account_id, **kwargs):
            async for frame in core_proxy.stream_responses(
                payload,
                headers,
                access_token,
                account_id,
                base_url=str(server.make_url("/")),
                session=session,
                upstream_stream_transport_override="http",
            ):
                yield frame

        monkeypatch.setattr(proxy_service, "core_stream_responses", stream_local)
        first_input = [developer] if prewarm else [developer, {"role": "user", "content": "Read key-17"}]
        first = await async_client.post(path, json={"model": "gpt-5.2", "input": first_input, "stream": True})
        assert first.status_code == 200, first.text
        follow = await async_client.post(
            path,
            json={
                "model": "gpt-5.2",
                "instructions": "",
                "input": [{"role": "user", "content": "Read key-17"}],
                "previous_response_id": "resp_chain_1",
                "stream": True,
            },
        )
        assert follow.status_code == 200, follow.text
        assert "34620" in follow.text
    assert len(observed) == 2
    assert observed[0]["input"] == first_input
    assert observed[0]["instructions"] == ""
    assert observed[1]["previous_response_id"] == "resp_chain_1"


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", ["/v1", "/backend-api/codex"])
@pytest.mark.parametrize("suffix", ["", "/"])
async def test_compact_keeps_developer_content_on_actual_upstream_wire(async_client, monkeypatch, prefix, suffix):
    await _import_plan(async_client, "plus")
    developer = {"role": "developer", "content": [{"type": "input_text", "text": "key-17=34620"}]}
    observed = []

    async def upstream(request):
        assert request.path == "/codex/responses"
        observed.append(await request.json())
        return web.json_response(
            {
                "object": "response.compact",
                "id": "resp_compact_developer",
                "output": [],
                "usage": {"input_tokens": 20, "output_tokens": 2},
            }
        )

    application = web.Application()
    application.router.add_post("/{tail:.*}", upstream)
    original_settings = core_proxy.get_settings()
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(application) as server, aiohttp.ClientSession() as session:
        monkeypatch.setattr(
            core_proxy,
            "get_settings",
            lambda: original_settings.model_copy(update={"upstream_base_url": str(server.make_url("/"))}),
        )

        async def compact_local(payload, headers, access_token, account_id, **kwargs):
            return await core_proxy.compact_responses(
                payload, headers, access_token, account_id, session=session, **kwargs
            )

        monkeypatch.setattr(proxy_service, "core_compact_responses", compact_local)
        response = await async_client.post(
            f"{prefix}/responses/compact{suffix}",
            json={
                "model": "gpt-5.2",
                "input": [developer, {"role": "user", "content": "Compact this history"}],
            },
            follow_redirects=False,
        )
        assert response.status_code == 200, response.text
    assert len(observed) == 1
    assert observed[0]["instructions"] == ""
    assert observed[0]["input"][0] == developer
