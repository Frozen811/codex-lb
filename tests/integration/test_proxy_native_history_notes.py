from __future__ import annotations

import json
from typing import Any

import pytest

import app.modules.proxy.service as proxy_module
from app.core.clients.proxy import CodexControlResponse, ProxyResponseError
from tests.integration.test_proxy_api_extended import _import_account

pytestmark = pytest.mark.integration

_HISTORY_OPERATIONS = (
    "list_windows",
    "list_items",
    "read_item",
    "search_contents",
)

_NOTES_OPERATIONS = (
    "list_files_by_prefix",
    "read_file",
    "search_contents",
    "append_to_file",
    "write_file",
    "thread_hint",
)


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", _HISTORY_OPERATIONS)
@pytest.mark.parametrize("prefix", ["/backend-api/codex", "/v1"])
async def test_native_history_v2_post_operations(async_client, monkeypatch, operation: str, prefix: str):
    await _import_account(async_client, f"acc_hist_{operation}", f"hist-{operation}@example.com")
    calls: list[dict[str, Any]] = []

    async def fake_codex_control(path, *, method, payload, query_params, headers, **kwargs):
        del headers, kwargs
        calls.append({"path": path, "method": method, "payload": payload, "query_params": query_params})
        return CodexControlResponse(
            status_code=200,
            body=json.dumps({"operation": operation, "status": "ok"}).encode(),
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr(proxy_module, "core_codex_control_request", fake_codex_control)
    payload = {"query": "test query", "window_id": "win_123"}

    response = await async_client.post(
        f"{prefix}/alpha/history/v2/{operation}",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json() == {"operation": operation, "status": "ok"}
    assert len(calls) == 1
    assert calls[0]["path"] == f"alpha/history/v2/{operation}"
    assert calls[0]["method"] == "POST"


@pytest.mark.asyncio
@pytest.mark.parametrize("operation", _NOTES_OPERATIONS)
@pytest.mark.parametrize("prefix", ["/backend-api/codex", "/v1"])
async def test_native_notes_v2_post_operations(async_client, monkeypatch, operation: str, prefix: str):
    await _import_account(async_client, f"acc_notes_{operation}", f"notes-{operation}@example.com")
    calls: list[dict[str, Any]] = []

    async def fake_codex_control(path, *, method, payload, query_params, headers, **kwargs):
        del headers, kwargs
        calls.append({"path": path, "method": method, "payload": payload, "query_params": query_params})
        return CodexControlResponse(
            status_code=200,
            body=json.dumps({"operation": operation, "status": "ok"}).encode(),
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr(proxy_module, "core_codex_control_request", fake_codex_control)
    payload = {"path": "notes.md", "content": "# Notes"}

    response = await async_client.post(
        f"{prefix}/alpha/notes/v2/{operation}",
        json=payload,
    )
    assert response.status_code == 200
    assert response.json() == {"operation": operation, "status": "ok"}
    assert len(calls) == 1
    assert calls[0]["path"] == f"alpha/notes/v2/{operation}"
    assert calls[0]["method"] == "POST"


@pytest.mark.asyncio
async def test_native_notes_v2_get_thread_hint(async_client, monkeypatch):
    await _import_account(async_client, "acc_notes_hint", "notes-hint@example.com")
    calls: list[dict[str, Any]] = []

    async def fake_codex_control(path, *, method, payload, query_params, headers, **kwargs):
        del headers, kwargs
        calls.append({"path": path, "method": method, "payload": payload, "query_params": query_params})
        return CodexControlResponse(
            status_code=200,
            body=b'{"thread_hint": "prior context summary"}',
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr(proxy_module, "core_codex_control_request", fake_codex_control)

    response = await async_client.get(
        "/backend-api/codex/alpha/notes/v2/thread_hint?thread_id=t_abc",
    )
    assert response.status_code == 200
    assert response.json() == {"thread_hint": "prior context summary"}
    assert len(calls) == 1
    assert calls[0]["path"] == "alpha/notes/v2/thread_hint"
    assert calls[0]["method"] == "GET"


@pytest.mark.asyncio
async def test_native_history_notes_trailing_slash_equivalent(async_client, monkeypatch):
    await _import_account(async_client, "acc_notes_slash", "notes-slash@example.com")
    calls: list[dict[str, Any]] = []

    async def fake_codex_control(path, *, method, payload, query_params, headers, **kwargs):
        del headers, kwargs
        calls.append({"path": path, "method": method, "payload": payload, "query_params": query_params})
        return CodexControlResponse(
            status_code=200,
            body=b'{"status": "ok"}',
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr(proxy_module, "core_codex_control_request", fake_codex_control)

    resp1 = await async_client.post(
        "/backend-api/codex/alpha/history/v2/list_windows/",
        json={},
    )
    assert resp1.status_code == 200
    assert calls[-1]["path"] == "alpha/history/v2/list_windows"

    resp2 = await async_client.get(
        "/v1/alpha/notes/v2/thread_hint/",
    )
    assert resp2.status_code == 200
    assert calls[-1]["path"] == "alpha/notes/v2/thread_hint"


@pytest.mark.asyncio
async def test_native_history_notes_unknown_operation_returns_404(async_client):
    response = await async_client.post(
        "/backend-api/codex/alpha/history/v2/unknown_operation",
        json={},
    )
    assert response.status_code == 404
    error = response.json()["error"]
    assert error["code"] == "not_found"
    assert "unknown_operation" in error["message"]


@pytest.mark.asyncio
async def test_native_history_notes_thread_identity_affinity(async_client, monkeypatch):
    await _import_account(async_client, "acc_thread_1", "thread-1@example.com")
    await _import_account(async_client, "acc_thread_2", "thread-2@example.com")
    captured_accounts: list[str | None] = []

    async def fake_codex_control(path, *, account_id, **kwargs):
        del path, kwargs
        captured_accounts.append(account_id)
        return CodexControlResponse(
            status_code=200,
            body=b'{"status": "ok"}',
            headers={"content-type": "application/json"},
        )

    monkeypatch.setattr(proxy_module, "core_codex_control_request", fake_codex_control)

    # First request binds thread_xyz to an account
    resp1 = await async_client.post(
        "/backend-api/codex/alpha/notes/v2/write_file",
        json={"content": "checkpoint"},
        headers={"thread-id": "thread_xyz"},
    )
    assert resp1.status_code == 200
    bound_account = captured_accounts[0]
    assert bound_account in ("acc_thread_1", "acc_thread_2")

    # Second request with the same thread-id stays with the same account
    resp2 = await async_client.get(
        "/backend-api/codex/alpha/notes/v2/thread_hint",
        headers={"thread-id": "thread_xyz"},
    )
    assert resp2.status_code == 200
    assert captured_accounts[1] == bound_account


@pytest.mark.asyncio
async def test_native_history_notes_unavailable_owner(async_client, monkeypatch):
    await _import_account(async_client, "acc_single_owner", "single-owner@example.com")

    async def fake_codex_control(*_args, **_kwargs):
        raise ProxyResponseError(503, {"error": {"code": "upstream_unavailable", "message": "Upstream unavailable"}})

    monkeypatch.setattr(proxy_module, "core_codex_control_request", fake_codex_control)

    response = await async_client.post(
        "/backend-api/codex/alpha/history/v2/read_item",
        json={"item_id": "item_123"},
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "upstream_unavailable"
