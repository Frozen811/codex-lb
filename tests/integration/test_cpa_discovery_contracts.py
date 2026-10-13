from __future__ import annotations

import asyncio

import pytest
from aiohttp import web
from sqlalchemy import select

from app.core.clients.http import get_http_client
from app.core.openai.model_refresh_scheduler import ModelRefreshScheduler
from app.core.openai.model_registry import get_model_registry
from app.db.models import ApiKeyUsageReservation, ModelSourceModel, RequestLog
from app.db.session import SessionLocal
from app.modules.model_sources import discovery
from tests.integration.model_source_helpers import _enable_api_key_auth, _free_port, stub_source_upstreams

pytestmark = pytest.mark.integration


@pytest.fixture
async def source_upstream():
    async with stub_source_upstreams() as start:
        yield start


def _catalog(*models: str):
    return {"models": [{"slug": model, "display_name": "Discovered", "context_window": 64000} for model in models]}


async def _source(client, base_url: str, *, name="cpa", models=None):
    response = await client.post(
        "/api/model-sources/",
        json={
            "name": name,
            "baseUrl": base_url,
            "apiKey": "synthetic-inference-key",
            "supportsResponses": True,
            "catalogMode": "cli_proxy_api",
            "models": models or [],
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["catalogMode"] == "cli_proxy_api"
    return response.json()["id"]


async def _models(source_id: str):
    async with SessionLocal() as session:
        rows = (
            await session.execute(select(ModelSourceModel).where(ModelSourceModel.source_id == source_id))
        ).scalars()
        return {row.model: (row.id, row.is_enabled, row.is_available, row.context_window) for row in rows}


@pytest.mark.asyncio
async def test_catalog_mode_is_explicit_and_defaults_to_manual(async_client):
    response = await async_client.post(
        "/api/model-sources/",
        json={"name": "manual", "baseUrl": "https://example.invalid/v1", "models": []},
    )
    assert response.status_code == 200, response.text
    assert response.json()["catalogMode"] == "manual"

    response = await async_client.post(
        "/api/model-sources/",
        json={"name": "cpa", "baseUrl": "https://example.invalid/v1", "catalogMode": "cli_proxy_api"},
    )
    assert response.status_code == 400, response.text


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_scheduled_discovery_catalogs_and_responses_without_native_accounts(async_client, source_upstream, path):
    requests = []

    async def handler(request):
        requests.append((request.path, dict(request.query), dict(request.headers)))
        if request.path.endswith("/models"):
            body = _catalog("discovered-external")
            body["models"][0]["api_key"] = "must-never-reach-catalog"
            return web.json_response(body)
        payload = await request.json()
        assert payload["model"] == "discovered-external"
        return web.json_response(
            {
                "id": "resp_cpa",
                "object": "response",
                "status": "completed",
                "output": [],
                "usage": {"input_tokens": 1, "output_tokens": 2, "total_tokens": 3},
            }
        )

    source_id = await _source(async_client, await source_upstream(handler))
    assert await _models(source_id) == {}
    assert await ModelRefreshScheduler(interval_seconds=300, enabled=True)._refresh_as_leader()
    assert (await _models(source_id))["discovered-external"][2:] == (True, 64000)
    for catalog_path in ["/v1/models", "/backend-api/codex/models"]:
        result = await async_client.get(catalog_path)
        assert result.status_code == 200, result.text
        assert "discovered-external" in result.text
        assert "must-never-reach-catalog" not in result.text
        assert "synthetic-inference-key" not in result.text
    response = await async_client.post(path, json={"model": "discovered-external", "input": "hello", "stream": False})
    assert response.status_code == 200, response.text
    assert response.json()["id"] == "resp_cpa"
    assert requests[0][0].endswith("/models")
    assert requests[0][1]["client_version"]
    assert requests[0][2]["Authorization"] == "Bearer synthetic-inference-key"


@pytest.mark.asyncio
async def test_catalog_omission_restoration_preserves_identity_and_manual_pause(async_client, source_upstream):
    catalog = _catalog("present", "paused")

    async def handler(request):
        return web.json_response(catalog)

    source_id = await _source(
        async_client, await source_upstream(handler), models=[{"model": "paused", "isEnabled": False}]
    )
    await discovery.refresh_source_catalogs()
    before = await _models(source_id)
    assert before["paused"][1:3] == (False, True)
    catalog = _catalog("new")
    await discovery.refresh_source_catalogs()
    after = await _models(source_id)
    assert after["present"][0] == before["present"][0]
    assert after["present"][2] is False
    for path in ["/v1/responses", "/backend-api/codex/responses", "/v1/responses/compact"]:
        response = await async_client.post(path, json={"model": "present", "input": "hello"})
        assert response.status_code == 503, response.text
        assert response.json()["error"]["code"] == "model_source_unavailable"
    async with SessionLocal() as session:
        assert not (await session.execute(select(ApiKeyUsageReservation))).scalars().all()
        assert not (await session.execute(select(RequestLog))).scalars().all()
    catalog = _catalog("present", "paused")
    await discovery.refresh_source_catalogs()
    restored = await _models(source_id)
    assert restored["present"][0] == before["present"][0]
    assert restored["present"][2] is True
    assert restored["paused"][1:3] == (False, True)


@pytest.mark.asyncio
@pytest.mark.parametrize("failure", ["invalid", "duplicate", "oversize", "redirect", "outage", "bounds", "shape"])
async def test_invalid_catalog_keeps_durable_last_good_rows(async_client, source_upstream, failure):
    valid = True
    redirected = []

    async def handler(request):
        if request.path.endswith("/redirected"):
            redirected.append(True)
        if valid:
            return web.json_response(_catalog("keep-me"))
        if failure == "invalid":
            return web.json_response({"models": [{"slug": "invalid", "context_window": "64000"}]})
        if failure == "duplicate":
            return web.json_response(_catalog("twice", "twice"))
        if failure == "oversize":
            return web.Response(body=b" " * (discovery._MAX_BODY_BYTES + 1))
        if failure == "redirect":
            raise web.HTTPFound(location="/redirected")
        if failure == "bounds":
            return web.json_response(_catalog(*[f"model-{i}" for i in range(1001)]))
        if failure == "shape":
            return web.json_response({"data": []})
        return web.Response(status=503)

    source_id = await _source(async_client, await source_upstream(handler))
    await discovery.refresh_source_catalogs()
    before = await _models(source_id)
    valid = False
    await discovery.refresh_source_catalogs()
    assert await _models(source_id) == before
    assert not redirected


@pytest.mark.asyncio
@pytest.mark.parametrize("edit", ["disable", "credential", "manual", "delete", "newer"])
async def test_catalog_result_is_fenced_after_configuration_changes(async_client, source_upstream, edit):
    async def handler(request):
        return web.json_response(_catalog("unused"))

    source_id = await _source(async_client, await source_upstream(handler))
    claimed = await discovery._claim_source(source_id)
    assert claimed is not None
    if edit == "delete":
        assert (await async_client.delete(f"/api/model-sources/{source_id}")).status_code == 204
    elif edit == "newer":
        assert await discovery._claim_source(source_id) is not None
    else:
        payload = {
            "disable": {"isEnabled": False},
            "credential": {"apiKey": "replacement"},
            "manual": {"catalogMode": "manual"},
        }[edit]
        response = await async_client.patch(f"/api/model-sources/{source_id}", json=payload)
        assert response.status_code == 200, response.text
    assert not await discovery._apply_catalog(claimed, discovery.SourceCatalog.model_validate(_catalog("stale")))
    assert await _models(source_id) == {}


@pytest.mark.asyncio
async def test_discovered_native_collision_preserves_registry_precedence_and_key_scope(async_client, source_upstream):
    model = next(iter(get_model_registry().get_models_with_fallback()))

    async def handler(request):
        return web.json_response(_catalog(model, "scoped-external"))

    source_id = await _source(async_client, await source_upstream(handler))
    await discovery.refresh_source_catalogs()
    from app.modules.model_sources.selection import select_responses_model_source

    assert await select_responses_model_source(model, None) is None
    assert await select_responses_model_source("scoped-external", None) is not None
    await _enable_api_key_auth(async_client)
    key = await async_client.post(
        "/api/api-keys/", json={"name": "scoped", "assignedSourceIds": [source_id], "allowedModels": ["another-model"]}
    )
    assert key.status_code == 200, key.text
    response = await async_client.post(
        "/v1/responses",
        json={"model": "scoped-external", "input": "hello"},
        headers={"Authorization": f"Bearer {key.json()['key']}"},
    )
    assert response.status_code == 403, response.text


@pytest.mark.asyncio
async def test_discovery_cancellation_reclaims_all_workers(async_client, monkeypatch):
    for i in range(6):
        await _source(async_client, "https://example.invalid/v1", name=f"source-{i}")
    entered = asyncio.Event()
    active = 0
    started = 0

    async def blocked(source_id):
        nonlocal active, started
        active += 1
        started += 1
        if active == 4:
            entered.set()
        try:
            await asyncio.Event().wait()
        finally:
            active -= 1

    monkeypatch.setattr(discovery, "refresh_source_catalog", blocked)
    task = asyncio.create_task(discovery.refresh_source_catalogs())
    await asyncio.wait_for(entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert active == 0
    assert started == 4


@pytest.mark.asyncio
async def test_catalog_mode_edits_roll_back_invalid_configuration(async_client):
    source_id = await _source(async_client, "https://example.invalid/v1")
    for payload in [{"supportsResponses": False}, {"models": []}]:
        response = await async_client.patch(f"/api/model-sources/{source_id}", json=payload)
        assert response.status_code == 400, response.text
        listing = (await async_client.get("/api/model-sources/")).json()["sources"]
        source = next(source for source in listing if source["id"] == source_id)
        assert source["catalogMode"] == "cli_proxy_api"
        assert source["supportsResponses"] is True
    switched = await async_client.patch(
        f"/api/model-sources/{source_id}",
        json={"catalogMode": "manual", "supportsResponses": False, "models": [{"model": "manual-model"}]},
    )
    assert switched.status_code == 200, switched.text
    assert switched.json()["catalogMode"] == "manual"
    assert switched.json()["models"][0]["isAvailable"] is True


@pytest.mark.asyncio
async def test_unreachable_catalog_keeps_existing_models(async_client):
    source_id = await _source(async_client, f"http://127.0.0.1:{_free_port()}/v1", models=[{"model": "previous"}])
    before = await _models(source_id)
    await discovery.refresh_source_catalogs()
    assert await _models(source_id) == before


@pytest.mark.asyncio
async def test_catalog_cancellation_closes_real_http_leases(async_client, source_upstream):
    entered = asyncio.Event()

    async def handler(request):
        response = web.StreamResponse(headers={"Content-Type": "application/json"})
        await response.prepare(request)
        await response.write(b'{"models":[')
        entered.set()
        await asyncio.Event().wait()
        return response

    url = await source_upstream(handler, handler_cancellation=True, shutdown_timeout=0.2)
    source_id = await _source(async_client, url)
    task = asyncio.create_task(discovery.refresh_source_catalogs())
    await asyncio.wait_for(entered.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert await _models(source_id) == {}
    client = get_http_client()
    source_session = client.model_source_session or client.session
    assert source_session.connector is not None
    assert not source_session.connector._acquired


@pytest.mark.asyncio
async def test_refresh_timeout_cancels_waiting_workers(async_client, monkeypatch):
    await _source(async_client, "https://example.invalid/v1")
    reclaimed = asyncio.Event()

    async def blocked(source_id):
        try:
            await asyncio.Event().wait()
        finally:
            reclaimed.set()

    monkeypatch.setattr(discovery, "refresh_source_catalog", blocked)
    monkeypatch.setattr(discovery, "_REFRESH_SECONDS", 0.05)
    await asyncio.wait_for(discovery.refresh_source_catalogs(), 2)
    assert reclaimed.is_set()
