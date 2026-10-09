from __future__ import annotations

import json

import aiohttp
import pytest
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.clients.proxy import CodexControlResponse, ProxyResponseError
from app.core.openai.model_registry import get_model_registry
from app.core.openai.model_registry_store import (
    encode_registry_export,
    persist_registry_snapshot,
    reconcile_model_registry_from_store,
)
from app.db.models import Account, AccountStatus, StickySession, StickySessionKind
from app.db.session import SessionLocal
from app.modules.proxy.affinity import _codex_session_selection_key
from tests.integration.test_proxy_api_extended import _import_account
from tests.integration.test_v1_models import _make_upstream_model

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_astra_alias_inference_public_path(async_client, monkeypatch, path):
    await _import_account(async_client, "astra-alias", "astra-alias@example.com")
    calls = []

    async def upstream(payload, *args, **kwargs):
        calls.append((payload.model, payload.reasoning.effort, payload.service_tier))
        event = {
            "type": "response.completed",
            "response": {"id": "resp_astra_alias", "object": "response", "status": "completed", "output": []},
        }
        yield "data: " + json.dumps(event) + "\n\n"

    monkeypatch.setattr(proxy_module, "core_stream_responses", upstream)
    response = await async_client.post(
        path,
        json={"model": "gpt-6-astra-extra-high-fast", "input": "hello", "stream": True},
    )
    assert response.status_code == 200
    assert "response.completed" in response.text
    assert calls == [("gpt-6-astra", "high", "priority")]


@pytest.mark.parametrize("prefix", ["", "/backend-api"])
@pytest.mark.parametrize("suffix", ["", "/"])
@pytest.mark.parametrize("path", ["plugins/featured", "ps/plugins/list"])
async def test_plugin_equivalent_paths_preserve_upstream(async_client, monkeypatch, prefix, suffix, path):
    await _import_account(async_client, "catalog-owner", "catalog-owner@example.com")
    calls = []

    async def upstream(upstream_path, *, query_params, **kwargs):
        calls.append((upstream_path, list(query_params), kwargs["account_id"]))
        return CodexControlResponse(206, b'{"catalog":"partial"}', {"content-type": "application/json"})

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    response = await async_client.get(f"{prefix}/{path}{suffix}?scope=a&scope=b", follow_redirects=False)
    assert response.status_code == 206
    assert response.content == b'{"catalog":"partial"}'
    assert calls == [(path, [("scope", "a"), ("scope", "b")], "catalog-owner")]


@pytest.mark.parametrize("prefix", ["", "/backend-api"])
@pytest.mark.parametrize("suffix", ["", "/"])
async def test_plugin_alias_write_denied(async_client, monkeypatch, prefix, suffix):
    async def upstream(*args, **kwargs):
        pytest.fail("catalog write dispatched upstream")

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    response = await async_client.post(f"{prefix}/ps/plugins/list{suffix}", json={}, follow_redirects=False)
    assert response.status_code == 405


@pytest.mark.parametrize("path", ["/v1/models", "/backend-api/codex/models"])
async def test_astra_bootstrap_catalog_public_path(async_client, path):
    await get_model_registry().clear()
    response = await async_client.get(path)
    assert response.status_code == 200
    if path == "/v1/models":
        entries = {item["id"]: item for item in response.json()["data"]}
        assert entries["gpt-6-astra"]["context_length"] == 272_000
    else:
        entries = {item["slug"]: item for item in response.json()["models"]}
        astra = entries["gpt-6-astra"]
        assert astra["context_window"] == 272_000
        assert astra["max_context_window"] == 872_000
        assert astra["default_reasoning_level"] == "low"
        assert astra["default_service_tier"] is None
        assert astra["shell_type"] == "unified_exec"
        assert astra["tool_mode"] == "code_mode_only"
        assert astra["use_responses_lite"] is True
        assert astra["minimal_client_version"] == "0.153.0"
        assert [level["effort"] for level in astra["supported_reasoning_levels"]] == [
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
            "ultra",
        ]


async def test_spark_survives_authoritative_catalog_and_restore(async_client):
    registry = get_model_registry()
    models = [_make_upstream_model("gpt-5.6-luna")]
    await registry.update(
        {"pro": models},
        per_account_results={"pro-owner": ("pro", models)},
        active_account_plans={"pro-owner": "pro"},
    )
    encoded = encode_registry_export(await registry.export_state())
    async with SessionLocal() as session:
        await persist_registry_snapshot(session, encoded=encoded, leader_id="spark-test-leader")
    await registry.clear()
    assert await reconcile_model_registry_from_store(raise_on_error=True) is True
    for path in ("/v1/models", "/backend-api/codex/models"):
        response = await async_client.get(path)
        assert response.status_code == 200
        items = response.json()["data" if path == "/v1/models" else "models"]
        assert "gpt-5.3-codex-spark" in {item.get("id", item.get("slug")) for item in items}
    dashboard = await async_client.get("/api/models")
    assert dashboard.status_code == 200
    assert "gpt-5.3-codex-spark" in {item["id"] for item in dashboard.json()["models"]}


@pytest.mark.parametrize("prefix", ["/backend-api/codex", "/v1", "/backend-api/codex/v1"])
@pytest.mark.parametrize("body", [b"null", b"[]", b'"string"', b"{broken"])
async def test_native_object_validation_prevents_dispatch(async_client, monkeypatch, prefix, body):
    await _import_account(async_client, "body-validation", "body-validation@example.com")

    async def upstream(*args, **kwargs):
        pytest.fail("invalid native body dispatched")

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    response = await async_client.post(
        f"{prefix}/alpha/notes/v2/write_file/", content=body, headers={"content-type": "application/json"}
    )
    assert response.status_code == 400
    assert response.json()["error"]["type"] == "invalid_request_error"


async def test_native_body_session_inherits_and_keeps_owner(async_client, monkeypatch):
    await _import_account(async_client, "notes-a", "notes-a@example.com")
    await _import_account(async_client, "notes-b", "notes-b@example.com")
    async with SessionLocal() as session:
        # Use the actual ORM account id rather than the upstream account header.
        owner = await session.scalar(select(Account).where(Account.chatgpt_account_id == "notes-b"))
        assert owner is not None
        session.add(
            StickySession(
                key=_codex_session_selection_key("native-task"),
                kind=StickySessionKind.CODEX_SESSION,
                account_id=owner.id,
            )
        )
        await session.commit()
    body = json.dumps({"path": "notes.md", "context": {"session_id": "native-task"}}, indent=2).encode()
    calls = []

    async def upstream(path, *, account_id, payload, headers, **kwargs):
        assert payload == body
        assert headers["x-openai-encrypted-tool-arguments"] == "true"
        assert headers["x-openai-tool-output-truncation-policy"] == '{"Bytes":4000}'
        calls.append(account_id)
        return CodexControlResponse(200, b'{"ok":true}', {"content-type": "application/json"})

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    for process in ("process-a", "process-b"):
        response = await async_client.post(
            "/backend-api/codex/alpha/notes/v2/write_file",
            content=body,
            headers={
                "session-id": process,
                "content-type": "application/json",
                "x-openai-encrypted-tool-arguments": "true",
                "x-openai-tool-output-truncation-policy": '{"Bytes":4000}',
            },
        )
        assert response.status_code == 200
    assert calls == ["notes-b", "notes-b"]
    async with SessionLocal() as session:
        history_rows = list(
            (await session.scalars(select(StickySession).where(StickySession.key.contains(":history_session:")))).all()
        )
        assert len(history_rows) == 1
        assert history_rows[0].account_id == owner.id
        paused_owner = await session.get(Account, owner.id)
        assert paused_owner is not None
        paused_owner.status = AccountStatus.PAUSED
        await session.commit()
    response = await async_client.post(
        "/backend-api/codex/alpha/notes/v2/write_file",
        content=body,
        headers={"content-type": "application/json", "session-id": "process-c"},
    )
    assert response.status_code == 503
    assert calls == ["notes-b", "notes-b"]


@pytest.mark.parametrize(
    "status,code", [(429, "quota_exceeded"), (401, "invalid_api_key"), (502, "upstream_unavailable")]
)
async def test_native_failure_never_dispatches_another_account(async_client, monkeypatch, status, code):
    await _import_account(async_client, "local-a", "local-a@example.com")
    await _import_account(async_client, "local-b", "local-b@example.com")
    calls = []

    async def upstream(path, *, account_id, **kwargs):
        calls.append(account_id)
        if len(set(calls)) > 1:
            return CodexControlResponse(200, b'{"wrong_owner":true}', {"content-type": "application/json"})
        raise ProxyResponseError(status, {"error": {"code": code, "message": "synthetic owner error"}})

    async def fresh(self, account, **kwargs):
        return account

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    monkeypatch.setattr(proxy_module.ProxyService, "_ensure_fresh", fresh)
    response = await async_client.post(
        "/backend-api/codex/alpha/history/v2/read_item",
        json={"item_id": "item-a", "context": {"session_id": "owned-history"}},
    )
    assert response.status_code == status
    assert len(set(calls)) == 1


async def test_native_refresh_connection_failure_does_not_change_owner(async_client, monkeypatch):
    await _import_account(async_client, "refresh-a", "refresh-a@example.com")
    await _import_account(async_client, "refresh-b", "refresh-b@example.com")
    refreshed = []

    async def fresh(self, account, **kwargs):
        refreshed.append(account.id)
        if len(refreshed) == 1:
            raise aiohttp.ClientConnectionError("synthetic refresh failure")
        return account

    async def upstream(*args, **kwargs):
        pytest.fail("native refresh failure dispatched an operation")

    monkeypatch.setattr(proxy_module.ProxyService, "_ensure_fresh", fresh)
    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    response = await async_client.post(
        "/v1/alpha/notes/v2/write_file",
        json={"context": {"session_id": "refresh-task"}},
    )
    assert response.status_code == 502
    assert len(refreshed) == 1
