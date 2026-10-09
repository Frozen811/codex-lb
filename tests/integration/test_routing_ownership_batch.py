from __future__ import annotations

import errno
import logging
import time
from types import SimpleNamespace

import aiohttp
import pytest
from aiohttp.client_reqrep import ConnectionKey
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.clients.proxy import ProxyResponseError
from app.core.errors import openai_error
from app.core.upstream_proxy import ResolvedProxyEndpoint, ResolvedUpstreamRoute
from app.db.models import Account, AccountStatus, ApiKeyUsageReservation, StickySession, StickySessionKind
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from tests.integration.test_proxy_transient_retry import (
    _create_metered_proxy_key,
    _import_account,
    _sse_event,
    _success_sse_event,
)

pytestmark = pytest.mark.integration


async def _seed_accounts(client):
    a = await _import_account(client, "cipher_a", "cipher-a@example.com")
    b = await _import_account(client, "cipher_b", "cipher-b@example.com")
    async with SessionLocal() as session:
        session.add(StickySession(key="cipher-affinity", kind=StickySessionKind.PROMPT_CACHE, account_id=a))
        await session.commit()
    return a, b


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure",
    [
        "status",
        "frame",
        "healthy",
        "server_error",
        "wrong_prefix",
        "unknown_reasoning",
        "selection_quota",
        "selection_paused",
    ],
)
async def test_proven_bypass_reasoning_replay_requires_owner_quota(async_client, monkeypatch, failure):
    from app.modules.proxy._service.http_bridge import streaming as bridge_streaming

    a, _b = await _seed_accounts(async_client)
    service = get_proxy_service_for_app(async_client._transport.app)
    monkeypatch.setattr(bridge_streaming, "_ws_transport_payload_budget_bytes", lambda: 1)
    prior = [{"role": "user", "content": "first question"}]
    turn_state = "http_turn_reasoning_bypass"
    claimed = await service._durable_bridge.claim_live_session(
        session_key_kind="session_header",
        session_key_value="reasoning-bypass",
        api_key_id=None,
        instance_id="test-instance",
        owner_process_epoch="test-epoch",
        lease_ttl_seconds=60.0,
        account_id=a,
        model="gpt-5.1",
        service_tier=None,
        latest_turn_state=turn_state,
        latest_response_id="resp_prior",
        allow_takeover=True,
    )
    await service._durable_bridge.renew_live_session(
        session_id=claimed.session_id,
        api_key_id=None,
        instance_id="test-instance",
        owner_epoch=claimed.owner_epoch,
        lease_ttl_seconds=60.0,
        latest_turn_state=turn_state,
        latest_response_id="resp_prior",
        latest_input_item_count=1,
        latest_input_full_fingerprint=proxy_module._fingerprint_input_items(prior),
    )
    await service._durable_bridge.register_turn_state(
        session_id=claimed.session_id,
        api_key_id=None,
        instance_id="test-instance",
        owner_epoch=claimed.owner_epoch,
        lease_ttl_seconds=60.0,
        turn_state=turn_state,
    )
    reasoning = {"type": "reasoning", "id": "rs_prior", "encrypted_content": "opaque", "summary": []}
    if failure == "unknown_reasoning":
        reasoning["unknown_owner"] = "opaque"
    body = [
        *prior,
        reasoning,
        {"role": "assistant", "content": [{"type": "output_text", "text": "prior answer"}]},
        {"role": "user", "content": "next"},
    ]
    if failure == "wrong_prefix":
        body[0] = {"role": "user", "content": "wrong question"}
    if failure in {"status", "frame"}:
        from app.core.openai.requests import ResponsesRequest
        from app.modules.proxy.replay_safety import project_responses_input_for_auth_recovery

        initial = ResponsesRequest.model_validate({"model": "gpt-5.1", "instructions": "hi", "input": body})
        lookup = await service._durable_bridge.lookup_turn_state_target(turn_state=turn_state, api_key_id=None)
        assert lookup is not None
        assert bridge_streaming._verify_durable_full_resend(initial, lookup) is not None
        assert isinstance(initial.input, list)
        assert project_responses_input_for_auth_recovery(initial.input) is not None
    if failure in {"selection_quota", "selection_paused"}:
        from app.modules.proxy.account_cache import get_account_selection_cache

        async with SessionLocal() as session:
            owner = await session.get(Account, a)
            assert owner is not None
            owner.status = AccountStatus.QUOTA_EXCEEDED if failure == "selection_quota" else AccountStatus.PAUSED
            owner.reset_at = int(time.time()) + 3600
            await session.commit()
        get_account_selection_cache().invalidate()
    attempts = []

    async def stream(payload, headers, access_token, account_id, **kwargs):
        attempts.append((account_id, payload.model_dump_for_forwarding()["input"], dict(headers)))
        if account_id == "cipher_a" and failure != "healthy":
            error = openai_error("usage_limit_reached", "usage limit reached")
            if failure == "server_error":
                raise ProxyResponseError(
                    500, openai_error("server_error", "unexpected server failure"), failure_phase="status"
                )
            if failure == "frame":
                yield _sse_event({"type": "response.failed", "response": error})
                return
            raise ProxyResponseError(429, error, failure_phase="status")
        yield _success_sse_event()

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post(
        "/backend-api/codex/responses",
        headers={"x-codex-turn-state": turn_state},
        json={
            "model": "gpt-5.1",
            "instructions": "hi",
            "input": body,
            "stream": True,
        },
    )
    if failure in {"status", "frame"}:
        assert "response.completed" in response.text, response.text
        assert [account for account, _, _ in attempts] == ["cipher_a", "cipher_b"]
        assert not any(item.get("type") == "reasoning" for item in attempts[-1][1])
        assert "x-codex-turn-state" not in {key.lower() for key in attempts[-1][2]}
    elif failure == "healthy":
        assert "response.completed" in response.text
        assert [account for account, _, _ in attempts] == ["cipher_a"]
    elif failure == "selection_quota":
        assert "response.completed" in response.text, response.text
        assert [account for account, _, _ in attempts] == ["cipher_b"]
        assert not any(item.get("type") == "reasoning" for item in attempts[0][1])
        assert "x-codex-turn-state" not in {key.lower() for key in attempts[0][2]}
    else:
        assert "response.completed" not in response.text
        assert all(account == "cipher_a" for account, _, _ in attempts)
    if failure not in {"selection_quota", "selection_paused"}:
        assert attempts[0][1] == body
        assert "x-codex-turn-state" in {key.lower() for key in attempts[0][2]}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path",
    [
        "/v1/responses",
        "/v1/responses/",
        "/backend-api/codex/responses",
        "/backend-api/codex/responses/",
    ],
)
@pytest.mark.parametrize("item_type", ["reasoning", "compaction"])
@pytest.mark.parametrize("failure", ["status", "frame"])
async def test_ciphertext_only_quota_rejection_moves_unchanged(async_client, monkeypatch, path, item_type, failure):
    a, b = await _seed_accounts(async_client)
    attempts = []
    ciphertext = "opaque-secret-ciphertext"

    async def stream(payload, headers, access_token, account_id, **kwargs):
        attempts.append((account_id, payload.model_dump_for_forwarding()))
        if account_id == "cipher_a":
            error = {"code": "usage_limit_reached", "message": "Usage limit reached"}
            if failure == "status":
                raise ProxyResponseError(429, openai_error(error["code"], error["message"]), failure_phase="status")
            yield _sse_event({"type": "response.failed", "response": {"error": error}})
            return
        yield _success_sse_event("resp_cipher_ok")

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post(
        path,
        json={
            "model": "gpt-5.1",
            "instructions": "hi",
            "stream": True,
            "prompt_cache_key": "cipher-affinity",
            "input": [
                {"type": item_type, "id": "retained_id", "encrypted_content": ciphertext},
                {"role": "user", "content": "next question"},
            ],
        },
    )
    assert response.status_code == 200, response.text
    assert "response.completed" in response.text, response.text
    assert [account for account, _ in attempts] == ["cipher_a", "cipher_b"]
    assert attempts[1][1]["input"] == attempts[0][1]["input"]
    assert attempts[1][1]["input"][0]["encrypted_content"] == ciphertext
    service = get_proxy_service_for_app(async_client._transport.app)
    for account in (a, b):
        assert await service._load_balancer.account_pressure_snapshot(account) == (0, 0, 0.0)


@pytest.mark.asyncio
@pytest.mark.parametrize("code", ["invalid_encrypted_content", "invalid_request_error"])
async def test_original_ciphertext_rejection_does_not_claim_cross_account_failover(
    async_client, monkeypatch, caplog, code
):
    _a, b = await _seed_accounts(async_client)
    attempts = []

    async def stream(payload, headers, access_token, account_id, **kwargs):
        attempts.append(account_id)
        raise ProxyResponseError(
            400, openai_error(code, "The reasoning content cannot be decrypted"), failure_phase="status"
        )
        yield

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    with caplog.at_level(logging.WARNING):
        response = await async_client.post(
            "/v1/responses",
            json={
                "model": "gpt-5.1",
                "instructions": "hi",
                "stream": True,
                "prompt_cache_key": "cipher-affinity",
                "input": [{"type": "compaction", "encrypted_content": "opaque"}],
            },
        )
    assert response.status_code == 400 and code in response.text
    assert attempts == ["cipher_a"]
    assert "cross_account_encrypted_reasoning_rejected" not in caplog.text
    service = get_proxy_service_for_app(async_client._transport.app)
    assert b not in service._load_balancer._runtime or service._load_balancer._runtime[b].error_count == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("first_poll_failed", [False, True])
@pytest.mark.parametrize("pinned", [False, True])
async def test_file_finalize_poll_operation_retains_its_owner(async_client, monkeypatch, first_poll_failed, pinned):
    import app.core.clients.codex as codex_module
    import app.core.clients.files as files_module

    a, b = await _seed_accounts(async_client)
    service = get_proxy_service_for_app(async_client._transport.app)
    if pinned:
        await service._pin_file_account("file_poll_operation", a)
    calls = []
    first_owner = None
    key = ConnectionKey("proxy.invalid", 8080, False, False, None, None, None)

    class Session:
        async def request(self, method, url, **kwargs):
            nonlocal first_owner
            account = kwargs["headers"]["chatgpt-account-id"]
            first_owner = first_owner or account
            calls.append(account)
            if account != first_owner:
                return SimpleNamespace(status=200, text='{"status":"success"}')
            if len(calls) == 1 and not first_poll_failed:
                return SimpleNamespace(status=200, text='{"status":"retry"}')
            raise aiohttp.ClientProxyConnectionError(key, ConnectionRefusedError(errno.ECONNREFUSED, "refused"))

        async def close(self):
            pass

    async def route(self, account, **kwargs):
        return ResolvedUpstreamRoute(
            "pool", "file-pool", ResolvedProxyEndpoint(f"timeout-{account.id}", "http", "proxy.invalid", 8080)
        )

    async def fresh(self, account, **kwargs):
        return account

    monkeypatch.setattr(codex_module, "discover_native_egress_client", lambda: None)
    monkeypatch.setattr(files_module, "create_codex_session", Session)
    monkeypatch.setattr(files_module, "_FILE_FINALIZE_POLL_DELAY_SECONDS", 0.0)
    monkeypatch.setattr(proxy_module.ProxyService, "_resolve_upstream_route_for_account", route)
    monkeypatch.setattr(proxy_module.ProxyService, "_ensure_fresh", fresh)
    response = await async_client.post("/backend-api/files/file_poll_operation/uploaded")
    if first_poll_failed and not pinned:
        assert response.status_code == 200, response.text
        assert len(calls) == 2 and calls[0] != calls[1]
    else:
        assert response.status_code == 502, response.text
        assert calls == [first_owner] * (1 if first_poll_failed else 2)
    for account in (a, b):
        assert await service._load_balancer.account_pressure_snapshot(account) == (0, 0, 0.0)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "boundary", ["file", "pinned_file", "unknown", "conversation", "visible", "burst", "ambiguous", "ambiguous_quota"]
)
async def test_ciphertext_exception_does_not_release_independent_or_executed_state(async_client, monkeypatch, boundary):
    a, b = await _seed_accounts(async_client)
    attempts = []
    item = {"type": "compaction", "encrypted_content": "opaque-bound"}
    payload = {
        "model": "gpt-5.1",
        "instructions": "hi",
        "stream": True,
        "prompt_cache_key": "cipher-affinity",
        "input": [item, {"role": "user", "content": "next"}],
    }
    if boundary in {"file", "pinned_file"}:
        payload["input"].append({"type": "input_file", "file_id": "opaque_unregistered_file"})
        if boundary == "pinned_file":
            service = get_proxy_service_for_app(async_client._transport.app)
            await service._pin_file_account("opaque_unregistered_file", a)
    elif boundary == "unknown":
        item["unrecognized_owner"] = "resource-secret"
    elif boundary == "conversation":
        payload["conversation"] = "conv_owned"

    async def stream(payload, headers, access_token, account_id, **kwargs):
        attempts.append(account_id)
        if account_id != "cipher_a":
            yield _success_sse_event()
            return
        if boundary == "visible":
            yield _sse_event({"type": "response.created", "response": {"id": "resp_owned"}})
        if boundary == "ambiguous":
            raise ProxyResponseError(
                502, openai_error("upstream_unavailable", "Ambiguous body failure"), failure_phase="body_read"
            )
        if boundary == "burst":
            raise ProxyResponseError(429, {"error": {"message": "Too many requests"}}, failure_phase="status")
        if boundary == "ambiguous_quota":
            raise ProxyResponseError(
                429, openai_error("usage_limit_reached", "ambiguous rejection"), failure_phase="body_read"
            )
        raise ProxyResponseError(
            429, openai_error("usage_limit_reached", "usage limit reached"), failure_phase="status"
        )

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post("/backend-api/codex/responses", json=payload)
    assert "response.completed" not in response.text
    assert "cipher_b" not in attempts
    service = get_proxy_service_for_app(async_client._transport.app)
    for account in (a, b):
        assert await service._load_balancer.account_pressure_snapshot(account) == (0, 0, 0.0)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["status", "frame"])
async def test_ciphertext_quota_failover_settles_reservation_before_health(async_client, monkeypatch, failure):
    a, b = await _seed_accounts(async_client)
    key = await _create_metered_proxy_key(async_client, "cipher-key")
    service = get_proxy_service_for_app(async_client._transport.app)
    original_health = service._handle_stream_error
    health_calls = []

    async def health(account, *args, **kwargs):
        async with SessionLocal() as session:
            rows = (await session.execute(select(ApiKeyUsageReservation))).scalars().all()
            assert rows and all(row.status != "reserved" for row in rows)
        health_calls.append(account.id)
        return await original_health(account, *args, **kwargs)

    async def stream(payload, headers, access_token, account_id, **kwargs):
        if account_id == "cipher_a":
            error = {"code": "usage_limit_reached", "message": "usage limit reached"}
            if failure == "status":
                raise ProxyResponseError(429, openai_error(error["code"], error["message"]), failure_phase="status")
            yield _sse_event({"type": "response.failed", "response": {"error": error}})
            return
        yield _success_sse_event()

    monkeypatch.setattr(service, "_handle_stream_error", health)
    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    response = await async_client.post(
        "/v1/responses",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": "gpt-5.1",
            "instructions": "hi",
            "stream": True,
            "prompt_cache_key": "cipher-affinity",
            "input": [{"type": "compaction", "encrypted_content": "opaque"}, {"role": "user", "content": "next"}],
        },
    )
    assert "response.completed" in response.text, response.text
    assert health_calls == [a]
    async with SessionLocal() as session:
        rows = (await session.execute(select(ApiKeyUsageReservation))).scalars().all()
        assert len(rows) == 1 and rows[0].status == "finalized"
    for account in (a, b):
        assert await service._load_balancer.account_pressure_snapshot(account) == (0, 0, 0.0)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["status", "frame"])
@pytest.mark.parametrize("code", ["invalid_encrypted_content", "invalid_request_error"])
async def test_replacement_ciphertext_rejection_has_private_provenance_and_neutral_health(
    async_client,
    monkeypatch,
    caplog,
    failure,
    code,
):
    a, b = await _seed_accounts(async_client)
    attempts = []
    secret = "never-log-this-ciphertext"

    async def stream(payload, headers, access_token, account_id, **kwargs):
        attempts.append(account_id)
        if account_id == "cipher_a":
            raise ProxyResponseError(
                429, openai_error("usage_limit_reached", "usage limit reached"), failure_phase="status"
            )
        error = {"code": code, "message": "The reasoning content cannot be decrypted"}
        if failure == "status":
            raise ProxyResponseError(400, openai_error(code, error["message"]), failure_phase="status")
        yield _sse_event({"type": "response.failed", "response": {"error": error}})

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    with caplog.at_level(logging.WARNING):
        response = await async_client.post(
            "/backend-api/codex/responses",
            json={
                "model": "gpt-5.1",
                "instructions": "hi",
                "stream": True,
                "prompt_cache_key": "cipher-affinity",
                "input": [{"type": "compaction", "encrypted_content": secret}, {"role": "user", "content": "next"}],
            },
        )
    assert code in response.text, response.text
    assert attempts == ["cipher_a", "cipher_b"]
    logs = [
        record.getMessage()
        for record in caplog.records
        if "cross_account_encrypted_reasoning_rejected" in record.getMessage()
    ]
    assert len(logs) == 1
    assert f"source_account_id={a}" in logs[0]
    assert f"target_account_id={b}" in logs[0]
    assert "failover_trigger=previsible_rate_limit_or_quota" in logs[0]
    assert f"upstream_code={code}" in logs[0]
    assert secret not in caplog.text
    service = get_proxy_service_for_app(async_client._transport.app)
    runtime = service._load_balancer._runtime.get(b)
    assert runtime is None or runtime.error_count == 0
    async with SessionLocal() as session:
        target = (await session.execute(select(Account).where(Account.id == b))).scalar_one()
        assert target.status == AccountStatus.ACTIVE
    for account in (a, b):
        assert await service._load_balancer.account_pressure_snapshot(account) == (0, 0, 0.0)
