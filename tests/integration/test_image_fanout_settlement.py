from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import select

import app.modules.proxy.api as proxy_api
from app.core.clients.proxy import ProxyResponseError
from app.core.errors import openai_error
from app.db.models import ApiKeyLimit, ApiKeyUsageReservation
from app.db.session import SessionLocal
from app.modules.proxy.service import ProxyService
from tests.integration.test_proxy_images import _enable_api_key_auth, _sse

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("route", ["generations", "edits"])
@pytest.mark.parametrize(
    "failure",
    [
        "none",
        "upstream",
        "all_failed",
        "exception",
        "log",
        "cancel",
        "cancel_empty",
        "cancel_cleanup",
        "cancel_settle",
        "cancel_release",
    ],
)
async def test_image_fanout_settles_completed_usage(async_client, monkeypatch, route, failure):
    await _enable_api_key_auth(async_client)
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "fanout-settlement",
            "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 1_000_000}],
        },
    )
    assert created.status_code == 200
    key_id, key = created.json()["id"], created.json()["key"]
    entered = asyncio.Event()
    success_ready = asyncio.Event()
    critical_started = asyncio.Event()
    finish_critical = asyncio.Event()
    empty = failure in {"cancel_empty", "cancel_release"}
    cleaned: list[int] = []
    internal_reservations = []
    services: list[ProxyService] = []
    call_index = 0

    async def stream(self, payload, headers, **kwargs) -> AsyncIterator[str]:
        nonlocal call_index
        index = call_index
        call_index += 1
        services.append(self)
        internal_reservations.append(kwargs["api_key_reservation"])
        try:
            if empty or (index == 1 and failure.startswith("cancel")):
                entered.set()
                await asyncio.Event().wait()
            if failure == "all_failed" or (index == 1 and failure == "upstream"):
                raise ProxyResponseError(502, openai_error("upstream_error", "generation failed"))
            if index == 1 and failure == "exception":
                raise RuntimeError("private-exception-marker")
            yield _sse(
                {
                    "type": "response.completed",
                    "response": {
                        "id": f"fanout-{index}",
                        "status": "completed",
                        "output": [{"type": "image_generation_call", "status": "completed", "result": "B64"}],
                        "tool_usage": {
                            "image_gen": {
                                "input_tokens": 7,
                                "output_tokens": 13,
                                "input_tokens_details": {"cached_tokens": 2},
                            }
                        },
                    },
                }
            )
            success_ready.set()
        finally:
            if index == 1 and failure == "cancel_cleanup":
                critical_started.set()
                await finish_critical.wait()
            cleaned.append(index)

    rewrite = AsyncMock(side_effect=RuntimeError("log failure") if failure == "log" else None)
    monkeypatch.setattr(ProxyService, "stream_responses", stream)
    monkeypatch.setattr(ProxyService, "rewrite_request_log_model", rewrite)
    settle = ProxyService.settle_image_api_key_usage
    release = proxy_api._release_reservation
    settle_calls = 0
    release_calls = 0

    async def tracked_settle(self, *args, **kwargs):
        nonlocal settle_calls
        settle_calls += 1
        if failure == "cancel_settle":
            critical_started.set()
            await finish_critical.wait()
        return await settle(self, *args, **kwargs)

    async def tracked_release(reservation):
        nonlocal release_calls
        release_calls += 1
        if failure == "cancel_release":
            critical_started.set()
            await finish_critical.wait()
        return await release(reservation)

    monkeypatch.setattr(ProxyService, "settle_image_api_key_usage", tracked_settle)
    monkeypatch.setattr(proxy_api, "_release_reservation", tracked_release)

    async def post():
        headers = {"Authorization": f"Bearer {key}"}
        if route == "generations":
            return await async_client.post("/v1/images/generations", headers=headers, json={"prompt": "draw", "n": 2})
        return await async_client.post(
            "/v1/images/edits",
            headers=headers,
            data={"prompt": "draw", "n": "2"},
            files={"image": ("source.png", b"\x89PNG\r\n\x1a\n" + b"\x00" * 16, "image/png")},
        )

    task = asyncio.create_task(post())
    try:
        if failure.startswith("cancel"):
            await asyncio.wait_for(entered.wait(), 5)
            if not empty:
                await asyncio.wait_for(success_ready.wait(), 5)
                # The collector exhausts the success stream before the next checkpoint.
                await asyncio.sleep(0)
            task.cancel()
            if failure in {"cancel_cleanup", "cancel_settle", "cancel_release"}:
                await asyncio.wait_for(critical_started.wait(), 5)
                task.cancel("repeated cancellation")
                await asyncio.sleep(0)
                assert not task.done()
                finish_critical.set()
            with pytest.raises(asyncio.CancelledError):
                await task
        else:
            response = await task
            expected_status = {"upstream": 502, "all_failed": 502, "exception": 500}.get(failure, 200)
            assert response.status_code == expected_status, response.text
            if failure == "exception":
                assert "private-exception-marker" not in response.text
                assert response.json()["error"]["code"] == "internal_error"
            if failure in {"none", "log"}:
                assert len(response.json()["data"]) == 2
                assert response.json()["usage"]["input_tokens_details"]["cached_tokens"] == 4
    finally:
        finish_critical.set()
        if not task.done():
            task.cancel()
        await asyncio.gather(task, return_exceptions=True)
        for service in set(services):
            assert await service.drain_persistence_tasks(timeout_seconds=5)

    assert sorted(cleaned) == [0, 1]
    assert internal_reservations == [None, None]
    successful_calls = (
        0
        if empty or failure == "all_failed"
        else 1
        if failure in {"upstream", "exception"} or failure.startswith("cancel")
        else 2
    )
    assert settle_calls == (1 if successful_calls else 0)
    assert release_calls == (0 if successful_calls else 1)
    async with SessionLocal() as session:
        rows = (
            (await session.execute(select(ApiKeyUsageReservation).where(ApiKeyUsageReservation.api_key_id == key_id)))
            .scalars()
            .all()
        )
        assert len(rows) == 1
        reservation = rows[0]
        assert reservation.status == ("finalized" if successful_calls else "released")
        if successful_calls:
            assert reservation.input_tokens == 7 * successful_calls
            assert reservation.output_tokens == 13 * successful_calls
            assert reservation.cached_input_tokens == 2 * successful_calls
        limit = (await session.execute(select(ApiKeyLimit).where(ApiKeyLimit.api_key_id == key_id))).scalar_one()
        assert limit.current_value == 20 * successful_calls
