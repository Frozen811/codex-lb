from __future__ import annotations

import asyncio
import copy
import json
import os
import time

import pytest
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.clients.proxy import ProxyResponseError
from app.core.errors import OpenAIErrorDetail, OpenAIErrorEnvelope
from app.core.openai.models import CompactResponsePayload
from app.db.models import ApiKeyUsageReservation, StickySession, StickySessionKind
from app.db.session import SessionLocal
from app.modules.usage.repository import UsageRepository
from tests.integration.off_loop_test_client import off_loop_test_client
from tests.integration.test_http_responses_bridge import (
    _cleanup_http_bridge_sessions,  # noqa: F401 - fixture owns bridge cleanup
    _FakeBridgeUpstreamWebSocket,
    _install_bridge_settings,
    _PrecreatedCloseUpstreamWebSocket,
)
from tests.integration.test_proxy_transient_retry import (
    _create_metered_proxy_key,
    _extract_events,
    _import_account,
    _success_sse_event,
)

pytestmark = pytest.mark.integration


class _ClosedUpstream(_PrecreatedCloseUpstreamWebSocket):
    async def send_text(self, text):
        await super().send_text(text)
        self.closed = True


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
@pytest.mark.parametrize("hard_owner", [False, True])
async def test_sticky_thread_moves_only_at_compaction(async_client, monkeypatch, path, hard_owner):
    owner = await _import_account(async_client, "boundary_owner", "boundary-owner@example.com")
    peer = await _import_account(async_client, "boundary_peer", "boundary-peer@example.com")
    current = (await async_client.get("/api/settings")).json()
    current.update(stickyReallocationTiming="after_compaction")
    assert (await async_client.put("/api/settings", json=current)).status_code == 200
    async with SessionLocal() as session:
        session.add(StickySession(key="boundary-key", kind=StickySessionKind.PROMPT_CACHE, account_id=owner))
        await session.commit()
        for account_id, pressure in [(owner, 96), (peer, 10)]:
            await UsageRepository(session).add_entry(
                account_id, pressure, window="primary", reset_at=int(time.time()) + 3600, window_minutes=300
            )
    selected = []

    async def stream(payload, headers, access_token, account_id, **kwargs):
        selected.append(account_id)
        yield _success_sse_event()

    async def compact(payload, headers, access_token, account_id, **kwargs):
        selected.append(account_id)
        return CompactResponsePayload.model_validate({"object": "response.compaction", "output": []})

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    monkeypatch.setattr(proxy_module, "core_compact_responses", compact)
    body = {
        "model": "gpt-5.1",
        "instructions": "",
        "input": "hello",
        "prompt_cache_key": "boundary-key",
        "stream": True,
    }
    response = await async_client.post(path, json=body)
    assert response.status_code == 200, response.text
    assert _extract_events(response.text.splitlines())[-1]["type"] == "response.completed"
    assert selected == ["boundary_owner"]
    async with SessionLocal() as session:
        row = await session.get(StickySession, ("boundary-key", StickySessionKind.PROMPT_CACHE))
        assert row is not None
        assert row.account_id == owner
    compact_body = dict(body, input=[], stream=False)
    if hard_owner:
        from app.dependencies import get_proxy_service_for_app

        await get_proxy_service_for_app(async_client._transport.app).drain_persistence_tasks(timeout_seconds=5)
        compact_body["previous_response_id"] = "resp_ok"
    response = await async_client.post(
        path.rstrip("/") + "/compact" + ("/" if path.endswith("/") else ""), json=compact_body
    )
    assert response.status_code == 200, response.text
    assert selected == ["boundary_owner", "boundary_owner" if hard_owner else "boundary_peer"]
    async with SessionLocal() as session:
        row = await session.get(StickySession, ("boundary-key", StickySessionKind.PROMPT_CACHE))
        assert row is not None
        assert row.account_id == (owner if hard_owner else peer)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
@pytest.mark.parametrize("failure_shape", ["status", "event"])
@pytest.mark.parametrize("retained", ["inline", "reasoning", "compaction"])
async def test_previsible_image_quota_recovery_preserves_input_and_settles(
    async_client, monkeypatch, path, failure_shape, retained
):
    owner = await _import_account(async_client, "quota_owner", "quota-owner@example.com")
    await _import_account(async_client, "quota_peer", "quota-peer@example.com")
    key = await _create_metered_proxy_key(async_client, "image-quota")
    async with SessionLocal() as session:
        session.add(StickySession(key="image-quota-key", kind=StickySessionKind.PROMPT_CACHE, account_id=owner))
        await session.commit()
    image = {"type": "input_image", "image_url": "data:image/png;base64,iVBORw0KGgo="}
    items = [
        {"role": "user", "content": "first"},
        {"role": "assistant", "content": [{"type": "output_text", "text": "answer"}]},
    ]
    if retained == "reasoning":
        items.insert(1, {"type": "reasoning", "id": "rs_prior", "encrypted_content": "encrypted-prior", "summary": []})
    elif retained == "compaction":
        items.insert(0, {"type": "compaction", "encrypted_content": "opaque-checkpoint"})
    items.append({"role": "user", "content": [{"type": "input_text", "text": "follow up"}, image]})
    body = {
        "model": "gpt-5.1",
        "instructions": "",
        "input": items,
        "prompt_cache_key": "image-quota-key",
        "stream": True,
    }
    original = copy.deepcopy(body)
    assert isinstance(original["input"], list)
    attempts = []
    error: OpenAIErrorDetail = {"code": "usage_limit_reached", "message": "quota reached", "type": "insufficient_quota"}

    async def stream(payload, headers, access_token, account_id, **kwargs):
        attempts.append((account_id, payload.model_dump()))
        if account_id == "quota_owner":
            if failure_shape == "status":
                raise ProxyResponseError(429, OpenAIErrorEnvelope(error=error), failure_phase="status")
            yield proxy_module.format_sse_event(
                {"type": "response.failed", "response": {"object": "response", "status": "failed", "error": error}}
            )
            return
        yield _success_sse_event()

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post(path, json=body, headers={"Authorization": f"Bearer {key}"})
    assert response.status_code == 200, response.text
    events = _extract_events(response.text.splitlines())
    assert events[-1]["type"] == "response.completed", events
    assert [account for account, _ in attempts] == ["quota_owner", "quota_peer"]
    assert attempts[0][1]["input"] == original["input"]
    assert attempts[1][1]["input"][-1] == original["input"][-1]
    assert attempts[1][1]["input"] == original["input"]
    assert attempts[1][1]["prompt_cache_key"] == body["prompt_cache_key"]
    assert body == original
    async with SessionLocal() as session:
        reservations = list((await session.execute(select(ApiKeyUsageReservation))).scalars())
        assert len(reservations) == 1
        assert reservations[0].status == "finalized"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
async def test_bridge_slimming_preserves_file_tool_and_recent_turn(async_client, monkeypatch, path):
    _install_bridge_settings(monkeypatch, enabled=True)
    await _import_account(async_client, "slim_owner", "slim-owner@example.com")
    upstream = _FakeBridgeUpstreamWebSocket("resp_slim")

    async def connect(*args, **kwargs):
        return upstream

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    monkeypatch.setattr(proxy_module, "_UPSTREAM_RESPONSE_CREATE_MAX_BYTES", 3000)
    items = [
        {"role": "user", "content": [{"type": "input_file", "file_id": "file_kept"}]},
        {"type": "function_call", "call_id": "read", "name": "read", "arguments": "{}"},
        {"type": "function_call_output", "call_id": "read", "output": "x" * 100_000},
        {"role": "assistant", "content": [{"type": "output_text", "text": "historical answer"}]},
        {"role": "user", "content": "latest question"},
    ]
    response = await async_client.post(
        path,
        json={"model": "gpt-5.1", "instructions": "", "input": items, "prompt_cache_key": "slim-kept", "stream": True},
    )
    assert response.status_code == 200, response.text
    assert _extract_events(response.text.splitlines())[-1]["type"] == "response.completed"
    sent = json.loads(upstream.sent_text[0])
    assert len(sent["input"]) == len(items)
    for index in [0, 1, 3, 4]:
        assert sent["input"][index] == items[index]
    assert sent["input"][2]["call_id"] == "read"
    assert "historical tool output" in sent["input"][2]["output"]
    assert sent["prompt_cache_key"] == "slim-kept"


@pytest.mark.asyncio
async def test_timing_setting_is_strict_and_omission_preserves_it(async_client):
    assert (await async_client.get("/api/settings")).json()["stickyReallocationTiming"] == "immediate"
    response = await async_client.put("/api/settings", json={"stickyReallocationTiming": "after_compaction"})
    assert response.status_code == 200, response.text
    assert response.json()["stickyReallocationTiming"] == "after_compaction"
    response = await async_client.put("/api/settings", json={"stickyThreadsEnabled": False})
    assert response.status_code == 200
    assert response.json()["stickyReallocationTiming"] == "after_compaction"
    response = await async_client.put("/api/settings", json={"stickyReallocationTiming": "invalid"})
    assert response.status_code == 422
    assert (await async_client.get("/api/settings")).json()["stickyReallocationTiming"] == "after_compaction"


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_native_websocket_retains_pressured_owner_until_compact(async_client, app_instance, monkeypatch, path):
    owner = await _import_account(async_client, "ws_owner", "ws-owner@example.com")
    peer = await _import_account(async_client, "ws_peer", "ws-peer@example.com")
    key = await _create_metered_proxy_key(async_client, "ws-timing")
    response = await async_client.put("/api/settings", json={"stickyReallocationTiming": "after_compaction"})
    assert response.status_code == 200
    async with SessionLocal() as session:
        session.add(StickySession(key="ws-boundary", kind=StickySessionKind.PROMPT_CACHE, account_id=owner))
        await session.commit()
        for account_id, pressure in [(owner, 96), (peer, 10)]:
            await UsageRepository(session).add_entry(
                account_id, pressure, window="primary", reset_at=int(time.time()) + 3600, window_minutes=300
            )
    selected = []

    async def connect(headers, access_token, account_id, **kwargs):
        selected.append(account_id)
        return _FakeBridgeUpstreamWebSocket("resp_ws")

    async def compact(payload, headers, access_token, account_id, **kwargs):
        selected.append(account_id)
        return CompactResponsePayload.model_validate({"object": "response.compaction", "output": []})

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    monkeypatch.setattr(proxy_module, "core_compact_responses", compact)
    async with off_loop_test_client(app_instance, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        with client.websocket_connect(path, headers={"Authorization": f"Bearer {key}"}) as websocket:
            websocket.send_json(
                {
                    "type": "response.create",
                    "model": "gpt-5.1",
                    "instructions": "",
                    "input": "hello",
                    "prompt_cache_key": "ws-boundary",
                }
            )
            for _ in range(8):
                event = websocket.receive_json()
                if event["type"] == "response.completed":
                    break
            else:
                pytest.fail("Missing WebSocket completion")
        assert selected == ["ws_owner"]
        response = client.post(
            path + "/compact",
            json={"model": "gpt-5.1", "instructions": "", "input": [], "prompt_cache_key": "ws-boundary"},
            headers={"Authorization": f"Bearer {key}"},
        )
        assert response.status_code == 200, response.text
        assert selected == ["ws_owner", "ws_peer"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
async def test_repeated_orphan_output_preserves_client_anchor(async_client, monkeypatch, path):
    _install_bridge_settings(monkeypatch, enabled=True)
    await _import_account(async_client, "repeat_owner", "repeat-owner@example.com")
    upstream = _FakeBridgeUpstreamWebSocket("resp_repeat")

    async def connect(*args, **kwargs):
        return upstream

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    body = {"model": "gpt-5.1", "instructions": "", "input": "first", "prompt_cache_key": "reused-call", "stream": True}
    headers = {"session_id": "history-boundary-session", "thread-id": "history-boundary-thread"}
    assert (await async_client.post(path, json=body, headers=headers)).status_code == 200
    body["previous_response_id"] = "resp_repeat_1"
    body["input"] = [
        {"type": "function_call", "call_id": "reused", "name": "read", "arguments": "{}"},
        {"type": "function_call_output", "call_id": "reused", "output": "first result"},
        {"type": "function_call_output", "call_id": "reused", "output": "second result"},
    ]
    response = await async_client.post(path, json=body, headers=headers)
    assert response.status_code == 200, response.text
    assert _extract_events(response.text.splitlines())[-1]["type"] == "response.completed"
    assert len(upstream.sent_text) == 2
    sent = json.loads(upstream.sent_text[-1])
    assert sent["previous_response_id"] == "resp_repeat_1"
    assert sent["input"] == body["input"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
async def test_eventless_close_terminates_without_keepalive_only_stream(async_client, monkeypatch, path):
    _install_bridge_settings(monkeypatch, enabled=True)
    await _import_account(async_client, "closed_owner", "closed-owner@example.com")
    upstreams = []

    async def connect(*args, **kwargs):
        upstream = _ClosedUpstream(close_code=1000)
        upstreams.append(upstream)
        return upstream

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    response = await asyncio.wait_for(
        async_client.post(path, json={"model": "gpt-5.1", "instructions": "", "input": "first", "stream": True}),
        timeout=5,
    )
    if response.status_code == 200:
        events = _extract_events(response.text.splitlines())
        assert events[-1]["type"] == "response.failed", response.text
        assert events[-1]["response"]["error"]["code"] in {"stream_incomplete", "no_accounts"}
    else:
        assert response.status_code in {502, 503}, response.text
        assert response.json()["error"]["code"] in {"stream_incomplete", "no_accounts"}
    assert 1 <= len(upstreams) <= 2
    assert all(upstream.closed for upstream in upstreams)


@pytest.mark.asyncio
async def test_timing_migration_preserves_historical_default_and_roundtrips(tmp_path):
    from alembic import command
    from anyio import to_thread
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    from app.db.migrate import _build_alembic_config, check_schema_drift, run_upgrade

    db_url = os.environ.get("TIMING_MIGRATION_TEST_URL", f"sqlite+aiosqlite:///{tmp_path / 'timing.sqlite'}")
    parent = "20261010_000000_add_source_catalog_discovery"
    await to_thread.run_sync(lambda: run_upgrade(db_url, parent, bootstrap_legacy=False))
    engine = create_async_engine(db_url)
    try:
        async with engine.begin() as conn:
            assert (await conn.execute(text("SELECT COUNT(*) FROM dashboard_settings WHERE id=1"))).scalar_one() == 1
            await conn.execute(text("UPDATE dashboard_settings SET sticky_threads_enabled=false WHERE id=1"))
        await to_thread.run_sync(lambda: run_upgrade(db_url, "head", bootstrap_legacy=False))
        async with engine.begin() as conn:
            assert (
                await conn.execute(text("SELECT sticky_reallocation_timing FROM dashboard_settings"))
            ).scalar_one() == "immediate"
            await conn.execute(text("UPDATE dashboard_settings SET sticky_reallocation_timing='after_compaction'"))
        assert await to_thread.run_sync(lambda: check_schema_drift(db_url)) == ()
        await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(db_url), parent))
        await to_thread.run_sync(lambda: run_upgrade(db_url, "head", bootstrap_legacy=False))
        async with engine.connect() as conn:
            assert (
                await conn.execute(text("SELECT sticky_reallocation_timing FROM dashboard_settings"))
            ).scalar_one() == "immediate"
    finally:
        await engine.dispose()
