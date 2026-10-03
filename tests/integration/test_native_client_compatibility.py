from __future__ import annotations

import gzip

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer

import app.modules.proxy.service as proxy_module
from app.core.clients import proxy as core_proxy
from app.core.clients.proxy import CodexControlResponse
from tests.integration.test_proxy_api_extended import _import_account
from tests.integration.test_v1_models import _create_model_source, _populate_test_registry

pytestmark = pytest.mark.integration

_CONTROL_PREFIXES = ("/backend-api/codex", "/v1", "/backend-api/codex/v1")


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", _CONTROL_PREFIXES)
@pytest.mark.parametrize("suffix", ["", "/"])
async def test_search_alias_dispatches_without_redirect(async_client, monkeypatch, prefix, suffix):
    await _import_account(async_client, "search-alias-owner", "search-alias@example.com")
    calls = []
    body = b'{ "commands": {"search_query": [{"q": "synthetic search"}]} }'
    upstream_body = b'{"results":[{"title":"synthetic result"}]}'

    async def upstream(path, *, method, payload, query_params, **kwargs):
        calls.append((path, method, payload, list(query_params), kwargs["account_id"]))
        return CodexControlResponse(200, upstream_body, {"content-type": "application/json"})

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    response = await async_client.post(
        f"{prefix}/alpha/search{suffix}?tag=a&tag=b",
        content=body,
        headers={"content-type": "application/json"},
        follow_redirects=False,
    )
    assert response.status_code == 200
    assert response.json() == {"results": [{"title": "synthetic result"}]}
    assert calls == [("alpha/search", "POST", body, [("tag", "a"), ("tag", "b")], "search-alias-owner")]


@pytest.mark.asyncio
@pytest.mark.parametrize("suffix", ["", "/"])
@pytest.mark.parametrize("model_id", ["gpt-5.2", "vendor/model"])
async def test_individual_model_matches_catalog_with_slash(async_client, suffix, model_id):
    await _populate_test_registry()
    if model_id == "vendor/model":
        await _create_model_source(async_client, name="nested-model", model=model_id)
    listed = await async_client.get("/v1/models")
    expected = next(item for item in listed.json()["data"] if item["id"] == model_id)
    response = await async_client.get(f"/v1/models/{model_id}{suffix}", follow_redirects=False)
    assert response.status_code == 200
    actual = response.json()
    assert isinstance(actual.pop("created"), int)
    expected.pop("created")
    assert actual == expected


@pytest.mark.asyncio
@pytest.mark.parametrize("suffix", ["", "/"])
@pytest.mark.parametrize("scope", ["allowlist", "source", "both"])
async def test_individual_model_enforces_visibility_and_authentication(async_client, suffix, scope):
    visible_source_id = await _create_model_source(async_client, name="visible-source", model="vendor/visible")
    await _create_model_source(async_client, name="hidden-source", model="vendor/hidden")
    await _populate_test_registry()
    settings = await async_client.put("/api/settings", json={"apiKeyAuthEnabled": True})
    assert settings.status_code == 200
    key = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "model visibility",
            **({"assignedSourceIds": [visible_source_id]} if scope in {"source", "both"} else {}),
            **({"allowedModels": ["vendor/visible"]} if scope in {"allowlist", "both"} else {}),
        },
    )
    assert key.status_code == 200
    headers = {"Authorization": f"Bearer {key.json()['key']}"}
    visible = await async_client.get(f"/v1/models/vendor/visible{suffix}", headers=headers)
    assert visible.status_code == 200
    hidden_models = ["vendor/hidden", "unknown-model"]
    if scope != "source":
        hidden_models.append("gpt-5.2")
    for model_id in hidden_models:
        response = await async_client.get(f"/v1/models/{model_id}{suffix}", headers=headers)
        assert response.status_code == 404
        assert response.json()["error"]["code"] == "model_not_found"
        assert response.json()["error"]["param"] == "model"
    denied = await async_client.get(f"/v1/models/vendor/visible{suffix}")
    assert denied.status_code == 401


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", _CONTROL_PREFIXES)
@pytest.mark.parametrize("operation", ["alpha/history/v2/read_item", "alpha/notes/v2/write_file", "alpha/search"])
async def test_native_control_alias_authentication_and_scope(async_client, monkeypatch, prefix, operation):
    scoped_id = await _import_account(async_client, "scoped-owner", "scoped-owner@example.com")
    await _import_account(async_client, "excluded-owner", "excluded-owner@example.com")
    settings = await async_client.put("/api/settings", json={"apiKeyAuthEnabled": True})
    assert settings.status_code == 200
    key = await async_client.post(
        "/api/api-keys/", json={"name": "native scoped key", "assignedAccountIds": [scoped_id]}
    )
    assert key.status_code == 200
    calls = []

    async def upstream(path, *, account_id, **kwargs):
        calls.append((path, account_id))
        return CodexControlResponse(200, b'{"ok":true}', {"content-type": "application/json"})

    monkeypatch.setattr(proxy_module, "core_codex_control_request", upstream)
    path = f"{prefix}/{operation}/"
    denied = await async_client.post(path, json={})
    assert denied.status_code == 401
    assert calls == []
    accepted = await async_client.post(path, json={}, headers={"Authorization": f"Bearer {key.json()['key']}"})
    assert accepted.status_code == 200
    assert calls == [(operation, "scoped-owner")]


@pytest.mark.asyncio
@pytest.mark.parametrize("prefix", _CONTROL_PREFIXES)
@pytest.mark.parametrize("operation", ["alpha/search", "alpha/notes/v2/write_file"])
async def test_control_route_with_real_compressed_http_upstream(async_client, monkeypatch, prefix, operation):
    await _import_account(async_client, "http-owner", "http-owner@example.com")
    captured = []
    body = b'{ "opaque": "request bytes" }'
    response_body = b'{"results":[{"title":"local upstream result"}]}'

    async def handle(request):
        captured.append(
            (
                request.path,
                await request.read(),
                list(request.query.items()),
                request.headers.getall("Content-Type"),
                request.headers["x-codex-encryption-key"],
            )
        )
        return web.Response(
            body=gzip.compress(response_body),
            headers={"Content-Type": "application/json", "Content-Encoding": "gzip", "Set-Cookie": "private=1"},
        )

    upstream_app = web.Application()
    upstream_app.router.add_post(f"/codex/{operation}", handle)
    async with TestServer(upstream_app) as server, aiohttp.ClientSession() as session:

        async def transport(path, **kwargs):
            kwargs["base_url"] = str(server.make_url("/")).rstrip("/")
            kwargs["route"] = None
            kwargs["session"] = session
            kwargs["allow_direct_egress"] = True
            return await core_proxy.codex_control_request(path, **kwargs)

        monkeypatch.setattr(proxy_module, "core_codex_control_request", transport)
        response = await async_client.post(
            f"{prefix}/{operation}/?tag=a&tag=b",
            content=body,
            headers={
                "content-type": "application/json",
                "user-agent": "codex_cli_rs/0.159.0",
                "x-codex-encryption-key": "synthetic-header",
            },
            follow_redirects=False,
        )

    assert response.status_code == 200
    assert response.content == response_body
    assert response.json()["results"]
    assert "content-encoding" not in response.headers
    assert "set-cookie" not in response.headers
    assert captured == [
        (f"/codex/{operation}", body, [("tag", "a"), ("tag", "b")], ["application/json"], "synthetic-header")
    ]
