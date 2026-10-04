from __future__ import annotations

import asyncio
import contextlib
import json
import time
from dataclasses import dataclass, field, replace

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from sqlalchemy import select
from starlette.requests import ClientDisconnect

from app.core.clients import proxy_websocket
from app.core.utils.sse import parse_sse_data_json
from app.db.models import Account, AccountStatus, ApiKeyUsageReservation
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import service as proxy_service
from app.modules.proxy._service.http_bridge import quarantine, request_submit, upstream_events
from app.modules.proxy._service.http_bridge.queues import _HTTPBridgeEventQueue
from tests.integration.test_bridge_continuation_contracts import _events, _user
from tests.integration.test_bridge_continuation_contracts import bridge_origin as _bridge_origin_fixture

pytestmark = pytest.mark.integration
bridge_origin = _bridge_origin_fixture


@dataclass
class _DeliveryOrigin:
    queues: list[_HTTPBridgeEventQueue] = field(default_factory=list)
    sent: asyncio.Event = field(default_factory=asyncio.Event)


@pytest.fixture
async def delivery_origin(bridge_origin, async_client, monkeypatch):
    state = _DeliveryOrigin()

    def new_queue(**kwargs):
        queue = _HTTPBridgeEventQueue(max_events=2, max_bytes=512)
        state.queues.append(queue)
        return queue

    monkeypatch.setattr(request_submit, "_new_http_bridge_event_queue", new_queue)
    settings = upstream_events._service_get_settings().model_copy(update={"stream_idle_timeout_seconds": 0.1})
    monkeypatch.setattr(upstream_events, "_service_get_settings", lambda: settings)

    async def upstream(request):
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        async for message in socket:
            if message.type != web.WSMsgType.TEXT:
                continue
            response_id = "resp_delivery"
            await socket.send_json(
                {"type": "response.created", "response": {"id": response_id, "status": "in_progress"}}
            )
            for index in range(6):
                await socket.send_json(
                    {"type": "response.output_text.delta", "response_id": response_id, "delta": str(index)}
                )
            await socket.send_json(
                {
                    "type": "response.completed",
                    "response": {
                        "id": response_id,
                        "status": "completed",
                        "output": [],
                        "usage": {"input_tokens": 1, "output_tokens": 6, "total_tokens": 7},
                    },
                }
            )
            state.sent.set()
        return socket

    origin = web.Application()
    origin.router.add_get("/codex/responses", upstream)
    async with TestServer(origin, shutdown_timeout=0.2) as server:

        async def connect(headers, token, account_id, **kwargs):
            return await proxy_websocket.connect_responses_websocket(
                headers, token, account_id, base_url=str(server.make_url("")), allow_direct_egress=True
            )

        monkeypatch.setattr(proxy_service, "connect_responses_websocket", connect)
        try:
            yield state
        finally:
            service = get_proxy_service_for_app(async_client._transport.app)
            for session in list(service._http_bridge_sessions.values()):
                await service._close_http_bridge_session(session)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses"])
@pytest.mark.parametrize("action", ["resume", "stall", "cancel", "write_error"])
async def test_real_bridge_paused_delivery_has_bounded_cleanup(
    async_client, app_instance, monkeypatch, bridge_origin, delivery_origin, path, action
):
    service = get_proxy_service_for_app(app_instance)
    paused = asyncio.Event()
    resume = asyncio.Event()
    messages = []
    body = json.dumps({"model": "gpt-5.1", "input": [_user("delivery")], "stream": True}).encode()
    received_body = False

    async def receive():
        nonlocal received_body
        if not received_body:
            received_body = True
            return {"type": "http.request", "body": body, "more_body": False}
        await asyncio.Event().wait()

    async def send(message):
        if message["type"] == "http.response.body" and message.get("body") and not paused.is_set():
            paused.set()
            await resume.wait()
            if action == "write_error":
                raise OSError("downstream writer disconnected")
        messages.append(message)

    headers = [(key.lower().encode(), value.encode()) for key, value in async_client.headers.items()]
    headers.extend([(b"content-type", b"application/json"), (b"session_id", b"delivery-contract")])
    scope = {
        "type": "http",
        "asgi": {"version": "3.0", "spec_version": "2.4"},
        "method": "POST",
        "scheme": "http",
        "path": path,
        "raw_path": path.encode(),
        "root_path": "",
        "query_string": b"",
        "headers": headers,
        "client": ("127.0.0.1", 12345),
        "server": ("test", 80),
        "http_version": "1.1",
        "state": {},
    }
    task = asyncio.create_task(app_instance(scope, receive, send))
    try:
        await asyncio.wait_for(paused.wait(), timeout=5)
        await asyncio.wait_for(delivery_origin.sent.wait(), timeout=5)
        queue = delivery_origin.queues[-1]
        assert queue.qsize() <= 2
        assert queue.queued_bytes <= 512
        if action == "resume":
            resume.set()
        elif action == "stall":
            for _ in range(100):
                if queue._closed:
                    break
                await asyncio.sleep(0.01)
            assert queue._closed, "a paused client must not block the reader indefinitely"
            # A different request succeeds while the first consumer is still paused.
            independent = await async_client.post(
                path,
                headers={"session_id": "independent-delivery"},
                json={"model": "gpt-5.1", "input": [_user("independent")], "stream": True},
            )
            assert independent.status_code == 200, independent.text
            assert _events(independent)[-1]["type"] == "response.completed"
            resume.set()
        elif action == "write_error":
            resume.set()
        else:
            # Cancellation exercises an owned product stream after its first
            # upstream output, rather than an initial heartbeat handoff.
            active_states = [
                request for session in service._http_bridge_sessions.values() for request in session.pending_requests
            ]
            assert active_states and active_states[0].response_id is not None
            task.cancel()
        with contextlib.suppress(asyncio.CancelledError, ClientDisconnect):
            await asyncio.wait_for(task, timeout=5)
        if action in {"resume", "stall"}:
            blocks = b"".join(message.get("body", b"") for message in messages).decode().split("\n\n")
            events = [event for block in blocks if (event := parse_sse_data_json(block)) is not None]
            if action == "resume":
                assert [event["delta"] for event in events if event["type"] == "response.output_text.delta"] == list(
                    "012345"
                )
                assert events[-1]["type"] == "response.completed"
            else:
                terminals = [event for event in events if event["type"] in {"response.failed", "response.completed"}]
                assert len(terminals) == 1
                assert terminals[0]["type"] == "response.failed"
                assert terminals[0]["response"]["error"]["code"] == "stream_idle_timeout"
        assert queue.queued_bytes == 0
        assert not queue._putters
        assert await service.drain_persistence_tasks(timeout_seconds=5)
        for _ in range(100):
            if await service._load_balancer.account_pressure_snapshot(bridge_origin.owner_id) == (0, 0, 0.0):
                break
            await asyncio.sleep(0.01)
        assert await service._load_balancer.account_pressure_snapshot(bridge_origin.owner_id) == (0, 0, 0.0)
        async with SessionLocal() as database:
            reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
            assert reservations and all(row.status in {"released", "finalized"} for row in reservations), [
                row.status for row in reservations
            ]
            account = await database.get(Account, bridge_origin.owner_id)
            assert account.status == AccountStatus.ACTIVE
    finally:
        resume.set()
        if not task.done():
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses"])
@pytest.mark.parametrize("race", ["first_failure", "replacement", "pruned_replacement"])
async def test_real_completion_preserves_quarantine_armed_during_settlement(
    async_client, app_instance, monkeypatch, bridge_origin, path, race
):
    service = get_proxy_service_for_app(app_instance)
    original_clear = service._clear_http_bridge_retry_circuit
    captured = []

    async def interleaved_clear(session, **kwargs):
        result = await original_clear(session, **kwargs)
        registry = quarantine._http_bridge_quarantine_registry(service)
        if race == "first_failure":
            quarantine._record_http_bridge_quarantine_eventless_timeout(service, session)
            owner = session
        else:
            quarantine._quarantine_http_bridge_session(service, session, reason="repeated_eventless_timeout")
            if race == "pruned_replacement":
                entry = registry[session.key]
                entry.quarantined_until = 0
                entry.last_touched_monotonic = time.monotonic() - 601
                quarantine._prune_http_bridge_quarantine_registry(registry, time.monotonic())
                assert session.key not in registry
            owner = replace(session)
            service._http_bridge_sessions[session.key] = owner
            quarantine._quarantine_http_bridge_session(service, owner, reason="repeated_eventless_timeout")
        captured.append((session.key, owner, registry[session.key].generation))
        return result

    monkeypatch.setattr(service, "_clear_http_bridge_retry_circuit", interleaved_clear)
    response = await async_client.post(
        path,
        headers={"session_id": "quarantine-settlement"},
        json={"model": "gpt-5.1", "input": [_user("complete")], "stream": True},
    )
    assert response.status_code == 200, response.text
    assert _events(response)[-1]["type"] == "response.completed"
    assert len(captured) == 1
    key, owner, generation = captured[0]
    entry = quarantine._http_bridge_quarantine_registry(service)[key]
    assert entry.generation == generation
    assert entry.owner_ref() is owner
    if race == "first_failure":
        assert entry.consecutive_eventless_timeouts == 1
    else:
        assert quarantine._http_bridge_session_key_quarantined(service, key)
        assert generation >= 2
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert await service._load_balancer.account_pressure_snapshot(bridge_origin.owner_id) == (0, 0, 0.0)
