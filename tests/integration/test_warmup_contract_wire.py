from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import cast

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from sqlalchemy import select

from app.core.clients import proxy as core_proxy
from app.core.config.settings import get_settings
from app.core.errors import openai_error
from app.core.usage.models import UsagePayload
from app.db.models import AccountLimitWarmup, RequestLog, UsageHistory
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.limit_warmup import service as limit_service
from app.modules.limit_warmup.repository import LimitWarmupRepository
from app.modules.limit_warmup.service import LimitWarmupRequestLogRepository, LimitWarmupService
from app.modules.proxy import service as proxy_service
from app.modules.request_logs.repository import RequestLogsRepository
from app.modules.usage import updater
from tests.integration.test_proxy_warmup import _create_api_key, _enable_api_key_auth, _import_account
from tests.unit.test_limit_warmup import FakeSender, _account, _settings

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("terminal", [None, "response.created", "response.completed"])
async def test_fallback_adapter_exhaustion_and_close(async_client, app_instance, monkeypatch, terminal):
    await _enable_api_key_auth(async_client)
    owner = await _import_account(async_client, "adapter-owner", "adapter@example.invalid")
    _, key = await _create_api_key(async_client, name="adapter-warmup")
    closed = []

    async def compact(*args, **kwargs):
        raise core_proxy.ProxyResponseError(404, openai_error("upstream_error", "compact unavailable"))

    async def stream(*args, **kwargs):
        try:
            if terminal is not None:
                yield f'data: {{"type":"{terminal}","response":{{"id":"resp_adapter"}}}}\n\n'
        finally:
            closed.append(True)

    monkeypatch.setattr(proxy_service, "core_compact_responses", compact)
    monkeypatch.setattr(proxy_service, "core_stream_responses", stream)
    response = await async_client.post("/v1/warmup", headers={"Authorization": f"Bearer {key}"}, json={"mode": "force"})
    assert response.status_code == 200
    successful = terminal == "response.completed"
    assert len(response.json()["submitted"]) == int(successful)
    assert closed == [True]
    if not successful:
        assert response.json()["failed"][0]["error_code"] == "stream_incomplete"
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert service._load_balancer._runtime[owner].inflight_streams == 0
    async with SessionLocal() as database:
        log = (await database.scalars(select(RequestLog))).one()
    assert log.status == ("success" if successful else "error")
    assert log.input_tokens is None and log.output_tokens is None


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/warmup", "/v1/warmup/force"])
@pytest.mark.parametrize("outcome", ["completed", "no_usage", "empty", "created", "failed", "incomplete", "non404"])
async def test_plain_warmup_fallback_wire(async_client, app_instance, monkeypatch, path, outcome):
    await _enable_api_key_auth(async_client)
    owner = await _import_account(async_client, "warmup-wire-owner", "warmup-wire@example.invalid")
    _, key = await _create_api_key(async_client, name="warmup-wire")
    calls = []

    async def upstream(request: web.Request) -> web.Response:
        body = await request.json()
        calls.append((request.path, request.headers.get("chatgpt-account-id"), body))
        if any(item.get("type") == "compaction_trigger" for item in body["input"]):
            return web.json_response(
                {"error": {"code": "upstream_error", "message": "compact unavailable"}},
                status=503 if outcome == "non404" else 404,
            )
        if "max_output_tokens" in body:
            return web.json_response({"error": {"message": "Unsupported parameter: max_output_tokens"}}, status=400)
        frames = {
            "completed": (
                'data: {"type":"response.completed","response":{"id":"resp_warmup",'
                '"usage":{"input_tokens":5,"output_tokens":3}}}\n\n'
            ),
            "no_usage": 'data: {"type":"response.completed","response":{"id":"resp_warmup"}}\n\n',
            "empty": "",
            "created": 'data: {"type":"response.created","response":{"id":"resp_warmup"}}\n\n',
            "failed": (
                'data: {"type":"response.failed","response":{"id":"resp_warmup",'
                '"error":{"code":"upstream_error","message":"failed"}}}\n\n'
            ),
            "incomplete": 'data: {"type":"response.incomplete","response":{"id":"resp_warmup"}}\n\n',
        }
        return web.Response(text=frames[outcome], content_type="text/event-stream")

    application = web.Application()
    application.router.add_post("/backend-api/codex/responses/compact", upstream)
    application.router.add_post("/backend-api/codex/responses", upstream)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(application) as server, aiohttp.ClientSession() as session:
        monkeypatch.setenv("CODEX_LB_UPSTREAM_BASE_URL", str(server.make_url("/backend-api")))
        get_settings.cache_clear()

        async def compact(payload, headers, access_token, account_id, **kwargs):
            return await core_proxy.compact_responses(
                payload, headers, access_token, account_id, session=session, **kwargs
            )

        async def stream(payload, headers, access_token, account_id, **kwargs):
            async for block in core_proxy.stream_responses(
                payload, headers, access_token, account_id, session=session, **kwargs
            ):
                yield block

        monkeypatch.setattr(proxy_service, "core_compact_responses", compact)
        monkeypatch.setattr(proxy_service, "core_stream_responses", stream)
        response = await async_client.post(path, headers={"Authorization": f"Bearer {key}"}, json={"mode": "force"})
        assert response.status_code == 200, response.text
        successful = outcome in {"completed", "no_usage"}
        result = response.json()
        assert len(result["submitted"]) == int(successful), result
        assert len(result["failed"]) == int(not successful), result
        assert len(calls) == (1 if outcome == "non404" else 2)
        assert all(account == "warmup-wire-owner" for _, account, _ in calls)
        if len(calls) == 2:
            assert calls[1][2]["stream"] is True and calls[1][2]["store"] is False
            assert "max_output_tokens" not in calls[1][2]
            assert all(item["type"] != "compaction_trigger" for item in calls[1][2]["input"] if "type" in item)
        service = get_proxy_service_for_app(app_instance)
        assert await service.drain_persistence_tasks(timeout_seconds=5)
        assert service._load_balancer._runtime[owner].inflight_streams == 0
        async with SessionLocal() as database:
            log = (await database.scalars(select(RequestLog))).one()
        assert log.account_id == owner and log.request_kind == "warmup"
        assert log.status == ("success" if successful else "error")
        assert (log.input_tokens, log.output_tokens) == ((5, 3) if outcome == "completed" else (None, None))
    get_settings.cache_clear()


@pytest.mark.asyncio
async def test_force_probe_real_wire_omits_unsupported_output_limit(async_client, monkeypatch):
    owner = await _import_account(async_client, "probe-wire-owner", "probe-wire@example.invalid")
    calls = []

    async def upstream(request: web.Request) -> web.Response:
        calls.append((request.headers.get("chatgpt-account-id"), await request.json()))
        return web.Response(text='data: {"type":"response.completed"}\n\n', content_type="text/event-stream")

    async def usage(**kwargs):
        return UsagePayload(plan_type="plus")

    monkeypatch.setattr(updater, "fetch_usage", usage)
    application = web.Application()
    application.router.add_post("/backend-api/codex/responses", upstream)
    async with TestServer(application) as server:
        monkeypatch.setenv("CODEX_LB_UPSTREAM_BASE_URL", str(server.make_url("/backend-api")))
        get_settings.cache_clear()
        response = await async_client.post(f"/api/accounts/{owner}/probe")
        assert response.status_code == 200, response.text
        assert response.json()["probeStatusCode"] == 200
        assert len(calls) == 1 and calls[0][0] == "probe-wire-owner"
        assert calls[0][1]["stream"] is True and calls[0][1]["store"] is False
        assert "max_output_tokens" not in calls[0][1]
    get_settings.cache_clear()


@pytest.mark.asyncio
@pytest.mark.parametrize("index", [0, 1, 2])
@pytest.mark.parametrize("window_minutes", [180, 300])
@pytest.mark.parametrize("sliding", [False, True])
async def test_idle_warmup_cycle_claim_survives_deadline_motion(db_setup, monkeypatch, index, window_minutes, sliding):
    duration = window_minutes * 60
    cycle_start = 1_700_000_000 // duration * duration
    slot = index * duration // 3
    accounts = [_account(f"cycle-{i}") for i in range(3)]
    owner = accounts[index]
    sender = FakeSender()
    settings = _settings(limit_warmup_staggered_idle_enabled=True, limit_warmup_cooldown_seconds=0)
    async with SessionLocal() as database:
        database.add_all(accounts)
        await database.commit()

    for cycle, offset in [(0, 0), (0, 121), (1, 0), (1, 121)]:
        now = datetime.fromtimestamp(cycle_start + cycle * duration + slot + offset, timezone.utc).replace(tzinfo=None)
        monkeypatch.setattr(limit_service, "utcnow", lambda: now)
        deadline = (
            int(now.replace(tzinfo=timezone.utc).timestamp()) + duration
            if sliding
            else cycle_start + (cycle + 1) * duration
        )
        entry = UsageHistory(
            account_id=owner.id,
            used_percent=0,
            reset_at=deadline,
            window="primary",
            window_minutes=window_minutes,
            recorded_at=now,
        )
        before = UsageHistory(
            account_id=owner.id,
            used_percent=0,
            reset_at=deadline - 30 if sliding else deadline,
            window="primary",
            window_minutes=window_minutes,
            recorded_at=now - timedelta(seconds=30),
        )
        async with SessionLocal() as database:
            service = LimitWarmupService(
                LimitWarmupRepository(database),
                cast(LimitWarmupRequestLogRepository, RequestLogsRepository(database)),
                sender=sender,
            )
            await service.run_after_usage_refresh(
                accounts=[owner],
                stagger_accounts=accounts,
                settings=settings,
                before_primary={owner.id: before},
                after_primary={owner.id: entry},
                before_secondary={},
                after_secondary={},
                refresh_started_at=now - timedelta(seconds=122),
            )
        assert len(sender.calls) == cycle + 1
    async with SessionLocal() as database:
        claims = (await database.scalars(select(AccountLimitWarmup).order_by(AccountLimitWarmup.id))).all()
    assert [(row.window, row.reset_at, row.status) for row in claims] == [
        ("primary_idle", cycle_start + duration, "succeeded"),
        ("primary_idle", cycle_start + 2 * duration, "succeeded"),
    ]
