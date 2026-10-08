from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from typing import Any, cast

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer
from sqlalchemy import select

from app.core.clients import proxy_websocket
from app.db.models import ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import service as proxy_service
from tests.integration.test_bridge_continuation_contracts import (
    _events,
    _user,
)
from tests.integration.test_bridge_continuation_contracts import (
    bridge_origin as _bridge_origin_fixture,
)

pytestmark = pytest.mark.integration
bridge_origin = _bridge_origin_fixture


@dataclass
class _TerminalOrigin:
    terminal: dict | None = None
    frames: list[dict] = field(default_factory=list)


@pytest.fixture
async def terminal_origin(bridge_origin, monkeypatch, async_client):
    state = _TerminalOrigin()

    async def upstream(request):
        socket = web.WebSocketResponse()
        await socket.prepare(request)
        async for message in socket:
            if message.type != web.WSMsgType.TEXT:
                continue
            state.frames.append(json.loads(message.data))
            if state.terminal is not None:
                await socket.send_json(state.terminal)
                continue
            await socket.send_json(
                {"type": "response.created", "response": {"id": "resp_retry_seed", "status": "in_progress"}}
            )
            await socket.send_json(
                {
                    "type": "response.completed",
                    "response": {
                        "id": "resp_retry_seed",
                        "status": "completed",
                        "output": [
                            {
                                "type": "message",
                                "id": "msg_retry_seed",
                                "role": "assistant",
                                "content": [{"type": "output_text", "text": "seed"}],
                            }
                        ],
                        "usage": {"input_tokens": 1, "output_tokens": 1, "total_tokens": 2},
                    },
                }
            )
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
@pytest.mark.parametrize("delay_terminal_publication", [False, True])
async def test_reason_only_incomplete_opens_durable_circuit_before_next_dispatch(
    async_client, app_instance, monkeypatch, bridge_origin, terminal_origin, path, delay_terminal_publication
):
    headers = {"session_id": "incomplete-circuit-route"}
    seed = await async_client.post(
        path, headers=headers, json={"model": "gpt-5.1", "input": [_user("seed")], "stream": True}
    )
    assert seed.status_code == 200, seed.text
    assert _events(seed)[-1]["type"] == "response.completed"
    service = get_proxy_service_for_app(app_instance)
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    terminal_claimed = asyncio.Event()
    publish_terminal = asyncio.Event()
    post_submit_checked = asyncio.Event()
    hold_second_submit = False
    if delay_terminal_publication:
        original_record = service._record_http_bridge_retry_circuit_failure
        original_submit = service._submit_http_bridge_request
        original_cooldown = service._http_bridge_precreated_retry_cooldown_seconds

        async def record(*args, **kwargs):
            count = await original_record(*args, **kwargs)
            if count == 2:
                terminal_claimed.set()
                await publish_terminal.wait()
            return count

        async def submit(*args, **kwargs):
            await original_submit(*args, **kwargs)
            if hold_second_submit:
                await asyncio.wait_for(terminal_claimed.wait(), timeout=5)

        async def cooldown(*args, **kwargs):
            remaining = await original_cooldown(*args, **kwargs)
            if terminal_claimed.is_set():
                post_submit_checked.set()
            return remaining

        monkeypatch.setattr(service, "_record_http_bridge_retry_circuit_failure", record)
        monkeypatch.setattr(service, "_submit_http_bridge_request", submit)
        monkeypatch.setattr(service, "_http_bridge_precreated_retry_cooldown_seconds", cooldown)
    terminal_origin.terminal = {
        "type": "response.incomplete",
        "response": {
            "id": "resp_incomplete_contract",
            "status": "incomplete",
            "incomplete_details": {"reason": "stream_incomplete"},
        },
    }
    body = {"model": "gpt-5.1", "input": [_user("next")], "stream": True, "previous_response_id": "resp_retry_seed"}
    for expected_count in (1, 2):
        body["input"] = [_user(f"next {expected_count}")]
        hold_second_submit = delay_terminal_publication and expected_count == 2
        if hold_second_submit:
            response_task = asyncio.create_task(async_client.post(path, headers=headers, json=body))
            try:
                await asyncio.wait_for(post_submit_checked.wait(), timeout=5)
            finally:
                publish_terminal.set()
                response = await asyncio.wait_for(response_task, timeout=10)
        else:
            response = await asyncio.wait_for(async_client.post(path, headers=headers, json=body), timeout=10)
        assert response.status_code == 200, response.text
        assert _events(response)[-1] == terminal_origin.terminal
        assert await service.drain_persistence_tasks(timeout_seconds=5)
        assert len(cast(Any, service)._http_bridge_retry_circuits) == 1
        key = next(iter(cast(Any, service)._http_bridge_retry_circuits))
        persisted = await service._durable_bridge.lookup_retry_circuit(
            session_key_kind=key.affinity_kind, session_key_value=key.affinity_key, api_key_id=key.api_key_id
        )
        assert persisted is not None
        assert persisted.consecutive_failures == expected_count
        if expected_count == 1:
            sent = len(terminal_origin.frames)
            duplicate = await async_client.post(path, headers=headers, json=body)
            assert duplicate.status_code == 200, duplicate.text
            if path.startswith("/v1/"):
                assert _events(duplicate)[-1] == terminal_origin.terminal
            assert len(terminal_origin.frames) == sent
    frames_before = len(terminal_origin.frames)
    assert persisted.cooldown_until_epoch > time.time()
    repeated_terminal = await async_client.post(path, headers=headers, json=body)
    assert repeated_terminal.status_code == 200, repeated_terminal.text
    if path.startswith("/v1/"):
        assert _events(repeated_terminal)[-1] == terminal_origin.terminal
    assert len(terminal_origin.frames) == frames_before
    assert await service.drain_persistence_tasks(timeout_seconds=5)
    assert await service._load_balancer.account_pressure_snapshot(bridge_origin.owner_id) == (0, 0, 0.0)
    async with SessionLocal() as database:
        reservations = list(await database.scalars(select(ApiKeyUsageReservation)))
        assert all(row.status in {"released", "finalized"} for row in reservations)
        logs = list(await database.scalars(select(RequestLog).order_by(RequestLog.id)))
        assert logs[0].status == "success"
        assert logs[1].status == "error"
