from __future__ import annotations

import json
from contextlib import nullcontext
from types import SimpleNamespace
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from app.core.clients.proxy_websocket import UpstreamWebSocketMessage
from app.core.types import JsonValue
from app.core.utils.sse import parse_sse_data_json
from app.modules.proxy import service as proxy_service
from tests.simulation.virtual_time import VirtualClock
from tests.unit.test_durable_bridge_sessions import async_session_factory as _session_factory_fixture
from tests.unit.test_durable_bridge_sessions import coordinator as _coordinator_fixture
from tests.unit.test_proxy_http_bridge import _make_bridge_session, _make_eventless_http_bridge_owner

pytestmark = pytest.mark.unit
async_session_factory = _session_factory_fixture
coordinator = _coordinator_fixture


@pytest.mark.asyncio
@pytest.mark.parametrize("interpreted", [False, True])
@pytest.mark.parametrize(
    ("reason", "explicit_code", "exclusion", "expected_count"),
    [
        ("stream_incomplete", None, None, 1),
        ("max_output_tokens", "stream_incomplete", None, 1),
        ("stream_incomplete", "invalid_request_error", None, 0),
        ("max_output_tokens", None, None, 0),
        ("content_filter", None, None, 0),
        (None, None, None, 0),
        ("stream_incomplete", None, "soft", 0),
        ("stream_incomplete", None, "prewarm", 0),
        ("stream_incomplete", None, "skip_log", 0),
        ("stream_incomplete", None, "started", 0),
        ("stream_incomplete", None, "safe_replay", 0),
    ],
)
async def test_incomplete_accounting_keeps_error_precedence_and_eligibility(
    monkeypatch: pytest.MonkeyPatch, coordinator, interpreted, reason, explicit_code, exclusion, expected_count
) -> None:
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    service._durable_bridge = coordinator
    session = _make_bridge_session(key_value="incomplete-boundary-matrix")
    request = _make_eventless_http_bridge_owner()
    if exclusion == "soft":
        session.key = proxy_service._HTTPBridgeSessionKey("prompt_cache_key", "incomplete-boundary-matrix", None)
    elif exclusion == "prewarm":
        request.request_kind = "prewarm"
    elif exclusion == "skip_log":
        request.skip_request_log = True
    elif exclusion == "started":
        request.response_event_count = 1
    elif exclusion == "safe_replay":
        request.fresh_upstream_request_text = '{"type":"response.create","input":"full history"}'
        request.fresh_upstream_request_is_retry_safe = True
    session.pending_requests.append(request)
    monkeypatch.setattr(service, "_finalize_websocket_request_state", AsyncMock())
    monkeypatch.setattr(service, "_http_bridge_effective_anchor_poison_detail", AsyncMock(return_value=None))

    response: dict[str, JsonValue] = {"id": "resp_boundary", "status": "incomplete"}
    if reason is not None:
        response["incomplete_details"] = {"reason": reason}
    if explicit_code is not None:
        response["error"] = {"code": explicit_code, "type": "server_error", "message": "test terminal"}
    payload: dict[str, JsonValue] = {"type": "response.incomplete", "response": response}
    text = json.dumps(payload)
    message = (
        UpstreamWebSocketMessage(
            kind="text", text=text, responses_interpreted=True, event_type="response.incomplete", payload=payload
        )
        if interpreted
        else None
    )
    await service._process_http_bridge_upstream_text(session, text, message=message)

    persisted = await coordinator.lookup_retry_circuit(
        session_key_kind=session.key.affinity_kind, session_key_value=session.key.affinity_key, api_key_id=None
    )
    assert (persisted.consecutive_failures if persisted else 0) == expected_count
    assert request.event_queue is not None
    delivered = await request.event_queue.get()
    assert delivered is not None and parse_sse_data_json(delivered) == payload
    # Reprocessing the same terminal after its request was claimed must not
    # create another failure, including when the native transport interpreted it.
    await service._process_http_bridge_upstream_text(session, text, message=message)
    repeated = await coordinator.lookup_retry_circuit(
        session_key_kind=session.key.affinity_kind, session_key_value=session.key.affinity_key, api_key_id=None
    )
    assert (repeated.consecutive_failures if repeated else 0) == expected_count


@pytest.mark.asyncio
@pytest.mark.parametrize("cooldown", [None, 0.0, -10.0, 9_999.0])
async def test_absent_or_elapsed_durable_cooldown_never_reserves_a_probe(cooldown: float | None) -> None:
    clock = VirtualClock(monotonic_value=100.0, epoch_value=10_000.0)
    service = proxy_service.ProxyService(cast(Any, nullcontext()), clock=clock)
    session = _make_bridge_session(key_value="cooldown-sentinel-boundaries")
    service._durable_bridge = SimpleNamespace(
        lookup_retry_circuit=AsyncMock(
            return_value=(
                SimpleNamespace(
                    consecutive_failures=3,
                    cooldown_until_epoch=cooldown,
                    last_detail="clean_close",
                    updated_at_epoch=9_990.0,
                    admission_generation=0,
                )
                if cooldown is not None
                else None
            )
        )
    )
    for _ in range(3):
        claimed: list[float] = []
        assert await service._http_bridge_precreated_retry_allowed(session, claimed_lease_out=claimed)
        assert claimed == []
        state = cast(Any, service)._http_bridge_retry_circuits.get(session.key)
        if state is not None:
            assert state.cooldown_until == 0.0
            assert state.half_open_until == 0.0
