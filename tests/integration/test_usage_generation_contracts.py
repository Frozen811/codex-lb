from __future__ import annotations

import json
from collections.abc import AsyncIterator
from datetime import timezone

import aiohttp
import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from sqlalchemy import select

from app.core.clients import proxy as core_proxy
from app.core.types import JsonValue
from app.core.utils.sse import CODEX_KEEPALIVE_FRAME, ParsedSseBlock, format_local_sse_event, parse_sse_data_json
from app.db.models import ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.api_keys.repository import ApiKeysRepository
from app.modules.api_keys.service import ApiKeysService
from app.modules.proxy import service as proxy_service
from app.modules.proxy._service import request_log as request_log_module
from tests.integration.model_source_helpers import _create_model_source, _enable_api_key_auth, stub_source_upstreams
from tests.integration.test_proxy_api_extended import _import_account
from tests.simulation.virtual_time import VirtualClock

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize("transport", ["http", "auto"])
@pytest.mark.parametrize("serialization", ["spaced", "escaped", "nested"])
@pytest.mark.parametrize(("writes", "input_cost"), [(None, 0.8), (-10, 0.8), (50_000, 0.925), (200_000, 1.0)])
async def test_native_wire_usage_and_generation_survive_serialization_and_cleanup(
    async_client, app_instance, monkeypatch, transport, serialization, writes, input_cost
) -> None:
    await _enable_api_key_auth(async_client)
    owner = await _import_account(async_client, "usage-wire-owner", "usage-wire@example.invalid")
    created = await async_client.post(
        "/api/api-keys/",
        json={
            "name": "wire-cost",
            "assignedAccountIds": [owner],
            "limits": [{"limitType": "cost_usd", "limitWindow": "weekly", "maxValue": 800_000}],
        },
    )
    assert created.status_code == 200
    key = created.json()
    frames: list[dict[str, JsonValue]] = [
        {"type": "response.created", "response": {"id": "resp_usage_wire", "status": "in_progress"}},
        {"type": "response.reasoning_summary_text.delta", "delta": "plan"},
        {"type": "response.output_text.delta", "metadata": {"delta": "metadata only"}, "delta": ""},
        {"type": "response.output_text.delta", "metadata": {"delta": ""}, "delta": "Привет"},
        {"type": "response.output_text.delta", "delta": " world"},
        {
            "type": "response.completed",
            "response": {
                "id": "resp_usage_wire",
                "model": "gpt-6-astra",
                "status": "completed",
                "output": [
                    {
                        "type": "message",
                        "role": "assistant",
                        "content": [{"type": "output_text", "text": "Привет world"}],
                    }
                ],
                "usage": {
                    "input_tokens": 100_000,
                    "output_tokens": 24,
                    "input_tokens_details": {"cached_tokens": 20_000},
                    "output_tokens_details": {"reasoning_tokens": 4},
                },
            },
        },
    ]
    completed_response = frames[-1]["response"]
    assert isinstance(completed_response, dict)
    if writes is not None:
        completed_usage = completed_response["usage"]
        assert isinstance(completed_usage, dict)
        input_details = completed_usage["input_tokens_details"]
        assert isinstance(input_details, dict)
        input_details["cache_write_tokens"] = writes

    def serialize(frame):
        text = json.dumps(frame, ensure_ascii=False, separators=(",", ":"))
        if frame["type"] == "response.output_text.delta":
            if serialization == "spaced":
                text = text.replace('"delta":', '"delta" : ')
            elif serialization == "escaped":
                text = text.replace('"delta":', '"\\u0064elta":')
        return text

    upstream_calls = []

    async def upstream(request: web.Request) -> web.StreamResponse:
        if request.method == "GET":
            socket = web.WebSocketResponse()
            await socket.prepare(request)
            async for message in socket:
                upstream_calls.append(json.loads(message.data))
                for frame in frames:
                    await socket.send_str(serialize(frame))
            return socket
        upstream_calls.append(await request.json())
        return web.Response(
            text="".join(f"event: {frame['type']}\ndata: {serialize(frame)}\n\n" for frame in frames),
            content_type="text/event-stream",
        )

    application = web.Application()
    application.router.add_route("*", "/codex/responses", upstream)
    clock = VirtualClock(monotonic_value=100.0)
    service = get_proxy_service_for_app(app_instance)
    monkeypatch.setattr(service, "_clock", clock)
    monkeypatch.setattr(core_proxy, "discover_native_egress_client", lambda: None)
    async with TestServer(application) as server, aiohttp.ClientSession() as session:

        async def actual_stream(payload, headers, access_token, account_id, **kwargs):
            offsets = iter([0.0, 0.125, 0.25, 0.5, 0.75, 1.0])
            async for block in core_proxy.stream_responses(
                payload,
                headers,
                access_token,
                account_id,
                base_url=str(server.make_url("/")),
                session=session,
                upstream_stream_transport_override=transport,
            ):
                clock.step_to(100.0 + next(offsets))
                yield block
            # Local cleanup after terminal receipt must not affect generation speed.
            clock.advance(2.0)

        monkeypatch.setattr(proxy_service, "core_stream_responses", actual_stream)
        response = await async_client.post(
            "/v1/responses",
            headers={"Authorization": f"Bearer {key['key']}"},
            json={"model": "gpt-6-astra", "input": "hi", "stream": True},
        )
        assert response.status_code == 200
        events = [
            event
            for block in response.text.split("\n\n")
            if (event := parse_sse_data_json(block)) is not None and event.get("type") != "codex.keepalive"
        ]
        assert [event["type"] for event in events] == [frame["type"] for frame in frames]
        actual_response = events[-1]["response"]
        assert isinstance(actual_response, dict)
        assert actual_response["usage"] == completed_response["usage"]
        assert [event["delta"] for event in events if event["type"] == "response.output_text.delta"] == [
            "",
            "Привет",
            " world",
        ]
        assert f"data: {serialize(frames[4])}\n\n" in response.text
        assert await service.drain_persistence_tasks(timeout_seconds=5)

        cost = input_cost + 0.02 + 0.0012
        async with SessionLocal() as database:
            log = (await database.scalars(select(RequestLog))).one()
            reservation = (await database.scalars(select(ApiKeyUsageReservation))).one()
            assert log.account_id == owner
            assert log.cache_write_input_tokens == writes
            assert log.cost_usd == pytest.approx(cost)
            assert log.output_tokens == 24 and log.reasoning_tokens == 4
            assert log.latency_first_token_ms == 125
            assert log.latency_first_upstream_event_ms == 0
            assert log.latency_response_created_ms == 0
            assert log.latency_first_output_ms == 500
            assert log.output_delta_count == 2
            assert log.latency_upstream_terminal_ms == 1000
            assert log.latency_ms == 3000
            assert reservation.status == "finalized"
            assert reservation.cache_write_input_tokens == (writes or 0)
            assert reservation.cost_microdollars == round(cost * 1_000_000)
            # CAS finalization must not count the same disjoint input twice.
            await ApiKeysService(ApiKeysRepository(database)).finalize_usage_reservation(
                reservation.id,
                model="gpt-6-astra",
                input_tokens=100_000,
                output_tokens=24,
                cached_input_tokens=20_000,
                cache_write_input_tokens=writes,
            )
            limits = await ApiKeysRepository(database).get_limits_by_key(key["id"])
            assert limits[0].current_value == round(cost * 1_000_000)
            date = log.requested_at.replace(tzinfo=timezone.utc).date().isoformat()

        logs = await async_client.get("/api/request-logs?limit=1")
        assert logs.status_code == 200
        row = logs.json()["requests"][0]
        assert row["generationTps"] == 40.0
        assert row["generationTpsStatus"] == "estimated"
        assert row["costBreakdown"] == pytest.approx(
            {
                "inputUsd": input_cost,
                "cachedInputUsd": 0.02,
                "outputUsd": 0.0012,
                "totalUsd": cost,
            }
        )
        report = await async_client.get(
            "/api/reports", params={"start_date": date, "end_date": date, "timezone": "UTC"}
        )
        assert report.status_code == 200
        day = report.json()["daily"][0]
        assert day["medianTps"] == 40.0 and day["tpsSampleCount"] == 1
        blocked = await async_client.post(
            "/v1/responses",
            headers={"Authorization": f"Bearer {key['key']}"},
            json={"model": "gpt-6-astra", "input": "hi", "stream": True},
        )
        assert blocked.status_code == 429
        assert blocked.json()["error"]["code"] == "rate_limit_exceeded"
        assert len(upstream_calls) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("responses_api", [False, True])
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("reasoning", [None, True, 2**31, 3])
async def test_source_optional_metadata_preserves_delivery_usage_and_unknown_reasoning(
    async_client, responses_api, stream, reasoning
) -> None:
    model = "source-usage-wire"
    usage: dict[str, JsonValue] = (
        {"input_tokens": 8, "output_tokens": 5, "input_tokens_details": {"cached_tokens": True}}
        if responses_api
        else {"prompt_tokens": 8, "completion_tokens": 5, "prompt_tokens_details": {"cached_tokens": True}}
    )
    if reasoning is not None:
        usage["output_tokens_details" if responses_api else "completion_tokens_details"] = {
            "reasoning_tokens": reasoning
        }
    body: dict[str, JsonValue] = (
        {
            "id": "resp_source_usage_wire",
            "model": model,
            "status": "completed",
            "output": [
                {"type": "message", "role": "assistant", "content": [{"type": "output_text", "text": "Привет"}]}
            ],
        }
        if responses_api
        else {
            "id": "chatcmpl_source_usage_wire",
            "object": "chat.completion",
            "model": model,
            "choices": [{"index": 0, "message": {"role": "assistant", "content": "Привет"}, "finish_reason": "stop"}],
        }
    )
    body["usage"] = usage
    body["metrics"] = {
        "time_to_first_token_ms": 20 if reasoning == 3 else 2_147_483_647,
        "generation_time_ms": 180,
    }
    event = {"type": "response.completed", "response": body} if responses_api else body
    wire = "\r\n".join("data: " + line for line in json.dumps(event, ensure_ascii=False, indent=2).splitlines())
    wire = (wire + "\r\n\r\n" + ("" if responses_api else "data: [DONE]\r\n\r\n")).encode()
    cuts = sorted({wire.index(b"\r") + 1, wire.index("Привет".encode()) + 1})

    async def upstream(request: web.Request) -> web.StreamResponse:
        if not stream:
            return web.json_response(body)
        response = web.StreamResponse(headers={"Content-Type": "text/event-stream"})
        await response.prepare(request)
        offset = 0
        for cut in [*cuts, len(wire)]:
            await response.write(wire[offset:cut])
            offset = cut
        await response.write_eof()
        return response

    async with stub_source_upstreams() as start:
        base_url = await start(upstream)
        source = await _create_model_source(
            async_client, name="usage-wire", model=model, base_url=base_url, supports_responses=responses_api
        )
        await _enable_api_key_auth(async_client)
        created = await async_client.post(
            "/api/api-keys/",
            json={
                "name": "source-usage-wire",
                "assignedSourceIds": [source],
                "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 1000}],
            },
        )
        assert created.status_code == 200
        key = created.json()
        request = {"model": model, "stream": stream}
        request["input" if responses_api else "messages"] = (
            "hi" if responses_api else [{"role": "user", "content": "hi"}]
        )
        response = await async_client.post(
            "/v1/responses" if responses_api else "/v1/chat/completions",
            json=request,
            headers={"Authorization": f"Bearer {key['key']}"},
        )
        assert response.status_code == 200
        if not stream:
            assert response.json() == body
        elif not responses_api:
            assert response.content == wire
        else:
            events = [
                event
                for block in response.text.split("\n\n")
                if (event := parse_sse_data_json(block)) is not None and event.get("type") == "response.completed"
            ]
            assert len(events) == 1
            actual_response = events[0]["response"]
            assert isinstance(actual_response, dict)
            assert actual_response["usage"] == usage
            assert actual_response["output"] == body["output"]

        async with SessionLocal() as database:
            log = (await database.scalars(select(RequestLog))).one()
            assert log.status == "success" and log.source == "model_source"
            assert log.model_source_id == source and log.account_id is None
            assert log.input_tokens == 8 and log.output_tokens == 5
            assert log.cached_input_tokens == 0
            assert log.reasoning_tokens == (3 if reasoning == 3 else None)
            assert log.latency_first_token_ms == (20 if reasoning == 3 else None)
            assert log.latency_ms == (200 if reasoning == 3 else None)
            assert log.latency_first_output_ms is None and log.output_delta_count is None
            reservation = (await database.scalars(select(ApiKeyUsageReservation))).one()
            assert reservation.status == "finalized"
            limits = await ApiKeysRepository(database).get_limits_by_key(key["id"])
            assert limits[0].current_value == 13
        logs = await async_client.get("/api/request-logs?limit=1")
        row = logs.json()["requests"][0]
        assert row["generationTpsStatus"] == ("legacy_estimate" if reasoning == 3 else "missing_usage")
        assert row["generationTps"] == (pytest.approx(2 * 1000 / 180) if reasoning == 3 else None)


@pytest.mark.asyncio
@pytest.mark.parametrize("responses_api", [False, True])
@pytest.mark.parametrize("invalid_count", [True, 2**31])
async def test_source_invalid_total_cannot_finalize_a_limited_key(async_client, responses_api, invalid_count) -> None:
    body = (
        {
            "id": "resp_bad_usage",
            "status": "completed",
            "output": [],
            "usage": {"input_tokens": invalid_count, "output_tokens": 5},
        }
        if responses_api
        else {
            "id": "chatcmpl_bad_usage",
            "choices": [],
            "usage": {"prompt_tokens": invalid_count, "completion_tokens": 5},
        }
    )

    async def upstream(request: web.Request) -> web.Response:
        return web.json_response(body)

    async with stub_source_upstreams() as start:
        source = await _create_model_source(
            async_client,
            name="invalid-usage",
            model="bad-usage-wire",
            base_url=await start(upstream),
            supports_responses=responses_api,
        )
        await _enable_api_key_auth(async_client)
        created = await async_client.post(
            "/api/api-keys/",
            json={
                "name": "bad-usage-wire",
                "assignedSourceIds": [source],
                "limits": [{"limitType": "total_tokens", "limitWindow": "weekly", "maxValue": 1000}],
            },
        )
        assert created.status_code == 200
        key = created.json()
        payload = {"model": "bad-usage-wire"}
        payload["input" if responses_api else "messages"] = (
            "hi" if responses_api else [{"role": "user", "content": "hi"}]
        )
        response = await async_client.post(
            "/v1/responses" if responses_api else "/v1/chat/completions",
            json=payload,
            headers={"Authorization": f"Bearer {key['key']}"},
        )
        assert response.status_code == 502
        assert response.json()["error"]["code"] == "usage_unavailable"
        async with SessionLocal() as database:
            log = (await database.scalars(select(RequestLog))).one()
            assert log.status == "error" and log.input_tokens is None
            reservation = (await database.scalars(select(ApiKeyUsageReservation))).one()
            assert reservation.status == "released"
            limits = await ApiKeysRepository(database).get_limits_by_key(key["id"])
            assert limits[0].current_value == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses"])
@pytest.mark.parametrize("case", ["keepalive", "local_failure", "upstream_error_local_id", "zero", "local_created"])
@pytest.mark.parametrize("disable_metrics", [False, True])
async def test_http_phase_provenance_persists_and_exports(
    async_client, app_instance, monkeypatch, path, case, disable_metrics
) -> None:
    await _import_account(async_client, "http-phase-owner", "http-phase@example.invalid")
    service = get_proxy_service_for_app(app_instance)
    clock = VirtualClock(monotonic_value=100.0)
    monkeypatch.setattr(service, "_clock", clock)
    admission = service._get_work_admission()
    original_acquire = admission.acquire_response_create

    async def delayed_admission():
        lease = await original_acquire()
        clock.advance(0.5)
        return lease

    monkeypatch.setattr(admission, "acquire_response_create", delayed_admission)

    def event(payload: dict[str, JsonValue], *, local_id: bool = False) -> ParsedSseBlock:
        return ParsedSseBlock(f"data: {json.dumps(payload)}\n\n", payload, response_id_is_local=local_id)

    async def controlled_stream(*_args: object, **_kwargs: object) -> AsyncIterator[str]:
        if case == "local_failure":
            clock.advance(0.25)
            yield format_local_sse_event(
                {
                    "type": "response.failed",
                    "response": {"id": "resp_local", "error": {"code": "invalid_request_error", "message": "local"}},
                }
            )
            return
        if case == "upstream_error_local_id":
            yield event(
                {
                    "type": "response.failed",
                    "response": {
                        "id": "resp_normalized",
                        "error": {"code": "invalid_request_error", "message": "origin"},
                    },
                },
                local_id=True,
            )
            return
        if case in {"keepalive", "local_created"}:
            if case == "keepalive":
                clock.advance(0.125)
                yield ": keepalive\n\n"
                yield CODEX_KEEPALIVE_FRAME
                clock.advance(0.125)
            else:
                clock.advance(0.25)
            yield event({"type": "response.in_progress", "response": {"id": "resp_phases"}})
            clock.advance(0.25)
        created: dict[str, JsonValue] = {"type": "response.created", "response": {"id": "resp_phases"}}
        yield format_local_sse_event(created) if case == "local_created" else event(created)
        clock.advance(0.5)
        yield event({"type": "response.output_text.delta", "delta": "hello"})
        clock.advance(0.5)
        yield event({"type": "response.completed", "response": {"id": "resp_phases"}})

    if disable_metrics:
        monkeypatch.setattr(request_log_module, "PROMETHEUS_AVAILABLE", False)
        monkeypatch.setattr(request_log_module, "proxy_phase_latency_seconds", None)
    histogram = request_log_module.proxy_phase_latency_seconds
    metrics_available = request_log_module.PROMETHEUS_AVAILABLE
    assert (histogram is not None) == metrics_available

    def phase_samples() -> dict[tuple[str, str], float]:
        totals: dict[tuple[str, str], float] = {}
        if histogram is None:
            return totals
        # The public protocol exposes observation; collection is optional and
        # belongs to the actual installed Prometheus exporter, not a fake.
        for metric in getattr(histogram, "collect")():
            for sample in metric.samples:
                if sample.labels.get("transport") != "http" or not sample.name.endswith(("_count", "_sum")):
                    continue
                assert set(sample.labels) == {"phase", "transport", "upstream_transport", "model_class"}
                key = (sample.labels["phase"], "count" if sample.name.endswith("_count") else "sum")
                totals[key] = totals.get(key, 0.0) + sample.value
        return totals

    before = phase_samples()
    monkeypatch.setattr(proxy_service, "core_stream_responses", controlled_stream)
    response = await async_client.post(path, json={"model": "gpt-6-astra", "input": "hi", "stream": True})
    assert response.status_code == 200
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    expected_first = {
        "keepalive": 250,
        "local_failure": None,
        "upstream_error_local_id": 0,
        "zero": 0,
        "local_created": 250,
    }[case]
    expected_created = {
        "keepalive": 500,
        "local_failure": None,
        "upstream_error_local_id": None,
        "zero": 0,
        "local_created": None,
    }[case]
    async with SessionLocal() as database:
        log = (await database.scalars(select(RequestLog))).one()
        assert log.latency_queue_ms == 500
        assert log.latency_first_upstream_event_ms == expected_first
        assert log.latency_response_created_ms == expected_created
        assert log.latency_first_token_ms == ({"keepalive": 1000, "zero": 500, "local_created": 1000}.get(case))
    after = phase_samples()
    for phase, expected in [("first_upstream_event", expected_first), ("response_created", expected_created)]:
        count = after.get((phase, "count"), 0) - before.get((phase, "count"), 0)
        total = after.get((phase, "sum"), 0) - before.get((phase, "sum"), 0)
        assert count == (0 if expected is None or not metrics_available else 1)
        assert total == pytest.approx(0 if expected is None or not metrics_available else expected / 1000)
