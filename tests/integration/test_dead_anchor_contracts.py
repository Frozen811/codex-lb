from __future__ import annotations

import asyncio
import json
import time
from typing import Any, cast

import pytest
from sqlalchemy import select, update

import app.modules.proxy.service as proxy_module
from app.db.models import Account, AccountStatus, ApiKeyLimit, ApiKeyUsageReservation, HttpBridgeSessionRecord
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy._service.http_bridge import retry_circuit as retry_circuit_module
from app.modules.proxy.load_balancer import CONTINUITY_OWNER_UNAVAILABLE, AccountSelection
from tests.integration import test_http_responses_bridge as bridge

pytestmark = pytest.mark.integration
PATHS = ["/backend-api/codex/responses", "/backend-api/codex/responses/", "/v1/responses", "/v1/responses/"]


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("status", [AccountStatus.PAUSED, AccountStatus.DEACTIVATED, AccountStatus.REAUTH_REQUIRED])
@pytest.mark.parametrize("keyed", [False, True])
async def test_dead_client_anchor_ignores_incidental_reset_and_full_history_recovers(
    async_client, app_instance, monkeypatch, path: str, status: AccountStatus, keyed: bool
) -> None:
    dashboard = bridge._make_dashboard_settings()
    dashboard.api_key_auth_enabled = keyed
    bridge._install_proxy_settings(
        monkeypatch, app_settings=bridge._make_app_settings(enabled=True), dashboard_settings=dashboard
    )
    owner_id = await bridge._import_account(async_client, "dead-anchor-owner", "dead-anchor-owner@example.com")
    healthy_id = await bridge._import_account(async_client, "dead-anchor-healthy", "dead-anchor-healthy@example.com")
    owner, healthy = await bridge._get_account(owner_id), await bridge._get_account(healthy_id)
    selected: list[str] = []
    sockets: list[Any] = []
    raw_attempts: list[bool] = []

    async def select_account(self, deadline, **kwargs):
        del self, deadline
        if kwargs.get("preferred_account_id") == owner.id:
            return AccountSelection(
                account=None, error_message="Owner unavailable", error_code=CONTINUITY_OWNER_UNAVAILABLE
            )
        account = owner if not selected else healthy
        selected.append(account.id)
        return AccountSelection(account=account, error_message=None, error_code=None)

    async def fresh(self, target, *, force=False, timeout_seconds):
        del self, force, timeout_seconds
        return target

    async def connect(*args, **kwargs):
        del args, kwargs
        upstream = bridge._FakeBridgeUpstreamWebSocket(f"resp_dead_anchor_{len(sockets)}")
        sockets.append(upstream)
        return upstream

    async def raw(*args, **kwargs):
        del args, kwargs
        raw_attempts.append(True)
        raise AssertionError("dead-anchor refusal must not route to raw HTTP")
        yield ""  # Preserve the upstream adapter's async-generator protocol.

    monkeypatch.setattr(proxy_module.ProxyService, "_select_account_with_budget", select_account)
    monkeypatch.setattr(proxy_module.ProxyService, "_ensure_fresh_with_budget", fresh)
    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    monkeypatch.setattr(proxy_module, "core_stream_responses", raw)
    service = get_proxy_service_for_app(app_instance)
    headers = {"session_id": "dead-anchor-session", "thread-id": "dead-anchor-thread"}
    if keyed:
        created = await async_client.post(
            "/api/api-keys/",
            json={
                "name": "dead-anchor-key",
                "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 200000}],
            },
        )
        assert created.status_code == 200, created.text
        headers["Authorization"] = f"Bearer {created.json()['key']}"
        enabled = await async_client.put(
            "/api/settings",
            json={
                "stickyThreadsEnabled": False,
                "preferEarlierResetAccounts": False,
                "totpRequiredOnLogin": False,
                "apiKeyAuthEnabled": True,
            },
        )
        assert enabled.status_code == 200, enabled.text

    def body(history, **extra):
        return {
            "model": "gpt-5.1",
            "instructions": "",
            "input": history,
            "prompt_cache_key": "dead-anchor-cache",
            "stream": True,
            **extra,
        }

    history = [{"role": "user", "content": "first turn"}]
    try:
        first = await async_client.post(path, headers=headers, json=body(history))
        assert first.status_code == 200 and "response.completed" in first.text, first.text
        dispatched = json.loads(sockets[0].sent_text[0])
        assert not dispatched.get("previous_response_id")
        async with SessionLocal() as session:
            owned = (await session.scalars(select(HttpBridgeSessionRecord))).one()
            anchor = owned.latest_response_id
            assert anchor
        await service.close_all_http_bridge_sessions()
        reset_at = int(time.time()) + 30
        async with SessionLocal() as session:
            await session.execute(
                update(Account)
                .where(Account.id == owner.id)
                .values(status=status, reset_at=reset_at, deactivation_reason="account_auth_invalidated")
            )
            await session.commit()

        denied = await async_client.post(
            path, headers=headers, json=body([{"role": "user", "content": "continue"}], previous_response_id=anchor)
        )
        assert denied.status_code == 404, denied.text
        error = denied.json()["error"]
        assert error["code"] == "bridge_previous_response_not_found"
        assert "resend the full conversation history" in error["message"]
        assert not raw_attempts and len(sockets) == 1
        async with SessionLocal() as session:
            retired = (await session.scalars(select(HttpBridgeSessionRecord))).one()
            assert retired.continuity_abandonment_scope
            original_marker = (retired.continuity_abandonment_scope, retired.continuity_abandoned_at)
            persisted_owner = await session.get(Account, owner.id)
            assert persisted_owner is not None and persisted_owner.status == status
            assert persisted_owner.reset_at == reset_at

        repeated = await async_client.post(
            path, headers=headers, json=body([{"role": "user", "content": "continue"}], previous_response_id=anchor)
        )
        assert repeated.status_code == 404, repeated.text
        assert repeated.json()["error"]["code"] == "bridge_previous_response_not_found"
        async with SessionLocal() as session:
            retired = (await session.scalars(select(HttpBridgeSessionRecord))).one()
            assert (retired.continuity_abandonment_scope, retired.continuity_abandoned_at) == original_marker

        history.extend(
            [
                {"role": "assistant", "content": [{"type": "output_text", "text": "OK"}]},
                {"role": "user", "content": "continue"},
            ]
        )
        recovered = await async_client.post(path, headers=headers, json=body(history))
        assert recovered.status_code == 200 and "response.completed" in recovered.text, recovered.text
        assert selected[-1] == healthy.id and len(sockets) == 2 and not raw_attempts
        recovered_wire = json.loads(sockets[-1].sent_text[-1])
        assert not recovered_wire.get("previous_response_id")
        assert [item["role"] for item in recovered_wire["input"]] == [item["role"] for item in history]
        assert recovered_wire["input"] == history
    finally:
        await service.close_all_http_bridge_sessions()
    if keyed:
        deadline = time.monotonic() + 5
        while True:
            async with SessionLocal() as session:
                reservations = list((await session.scalars(select(ApiKeyUsageReservation))).all())
            if reservations and all(row.status != "reserved" for row in reservations):
                break
            assert time.monotonic() < deadline, (
                f"Unsettled reservations: {[(row.id, row.status) for row in reservations]}"
            )
            await asyncio.sleep(0.01)
        assert len(reservations) == 4
        async with SessionLocal() as session:
            limit = (await session.scalars(select(ApiKeyLimit))).one()
            assert limit.current_value == 52


@pytest.mark.parametrize("path", PATHS)
async def test_submit_time_tombstone_refusal_releases_carriers_but_guards_deltas(
    async_client, app_instance, monkeypatch, path: str
) -> None:
    bridge._install_bridge_settings(monkeypatch, enabled=True)
    owner_id = await bridge._import_account(async_client, "tombstone-owner", "tombstone-owner@example.com")
    owner = await bridge._get_account(owner_id)
    upstream = bridge._FakeBridgeUpstreamWebSocket("resp_tombstone")
    bridge._install_bridge_account_upstream(monkeypatch, account=owner, upstream=upstream)
    service = get_proxy_service_for_app(app_instance)
    headers = {"session_id": "tombstone-session", "thread-id": "tombstone-thread"}
    history = [{"role": "user", "content": "first turn"}]

    def body(history):
        return {
            "model": "gpt-5.1",
            "instructions": "",
            "input": history,
            "prompt_cache_key": "tombstone-cache",
            "stream": True,
        }

    try:
        first = await async_client.post(path, headers=headers, json=body(history))
        assert first.status_code == 200 and "response.completed" in first.text
        async with SessionLocal() as session:
            record = (await session.scalars(select(HttpBridgeSessionRecord))).one()
            denied_anchor = record.latest_response_id
            assert denied_anchor
        original_submit = service._submit_http_bridge_request
        captured = []

        async def late_tombstone(session, **kwargs):
            if not captured:
                request_state = kwargs["request_state"]
                assert request_state.proxy_injected_previous_response_id
                assert request_state.previous_response_id == denied_anchor
                persisted = await service._durable_bridge.persist_retry_circuit(
                    session_key_kind=session.key.affinity_kind,
                    session_key_value=session.key.affinity_key,
                    api_key_id=session.key.api_key_id,
                    consecutive_failures=0,
                    cooldown_until_epoch=0,
                    last_detail="anchor_abandoned",
                    updated_at_epoch=time.time(),
                )
                assert persisted is not None
                state = retry_circuit_module._HTTPBridgeRetryCircuitState(last_touched_monotonic=time.monotonic())
                state.last_detail = "anchor_abandoned"
                runtime = cast(Any, service)
                async with runtime._http_bridge_retry_circuit_lock:
                    runtime._http_bridge_retry_circuits[session.key] = state
                captured.append(session)
            return await original_submit(session, **kwargs)

        monkeypatch.setattr(service, "_submit_http_bridge_request", late_tombstone)
        history.extend(
            [
                {"role": "assistant", "content": [{"type": "output_text", "text": "OK"}]},
                {"role": "user", "content": "second turn"},
            ]
        )
        refusal = await async_client.post(path, headers=headers, json=body(history))
        assert refusal.status_code == 404, refusal.text
        assert refusal.json()["error"]["code"] == "bridge_previous_response_not_found"
        assert len(upstream.sent_text) == 1
        live = captured[0]
        assert live.last_completed_response_id is None
        assert denied_anchor not in live.previous_response_ids
        async with SessionLocal() as session:
            record = (await session.scalars(select(HttpBridgeSessionRecord))).one()
            assert record.latest_response_id is None
        tombstone = await service._durable_bridge.lookup_retry_circuit(
            session_key_kind=live.key.affinity_kind,
            session_key_value=live.key.affinity_key,
            api_key_id=live.key.api_key_id,
        )
        assert tombstone is not None and tombstone.last_detail == "anchor_abandoned"

        delta = await async_client.post(path, headers=headers, json=body("delta without history"))
        assert delta.status_code == 404, delta.text
        assert delta.json()["error"]["code"] == "bridge_previous_response_not_found"
        assert len(upstream.sent_text) == 1
        recovered = await async_client.post(path, headers=headers, json=body(history))
        assert recovered.status_code == 200 and "response.completed" in recovered.text, recovered.text
        assert len(upstream.sent_text) == 2
        recovery = json.loads(upstream.sent_text[-1])
        assert not recovery.get("previous_response_id")
        assert recovery["input"] == history
    finally:
        await service.close_all_http_bridge_sessions()
