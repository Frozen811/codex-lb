from __future__ import annotations

import json
from functools import partial
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.clients.proxy_websocket import UpstreamWebSocketMessage
from app.db.models import Account
from app.db.session import SessionLocal
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import api as proxy_api
from app.modules.proxy import service as proxy_service
from tests.integration.test_direct_websocket_close_1009 import _seed_connected_account
from tests.integration.test_proxy_websocket_responses import _SequencedUpstreamWebSocket, _websocket_settings

pytestmark = pytest.mark.integration


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("after_output", [False, True])
@pytest.mark.parametrize(
    "ending,penalized",
    [
        ("close-none", False),
        ("close-1006", False),
        ("ended-error", False),
        ("unproven-error", True),
        ("authored-close", True),
    ],
)
def test_direct_terminal_provenance_controls_health_without_replay(
    app_instance, monkeypatch, path, after_output, ending, penalized
):
    events = [
        UpstreamWebSocketMessage(
            "text", text=json.dumps({"type": "response.created", "response": {"id": "resp_evidence"}})
        )
    ]
    events.append(
        UpstreamWebSocketMessage(
            "text",
            text=json.dumps(
                {
                    "type": "response.output_text.delta" if after_output else "response.reasoning_text.delta",
                    "response_id": "resp_evidence",
                    "delta": "partial",
                }
            ),
        )
    )
    # Use the adapter's positive structured marker. Missing close-code alone
    # must never confer provenance on a nonterminal error or binary frame.
    events.append(
        UpstreamWebSocketMessage(
            kind="error" if "error" in ending else "close",
            close_code=1006 if ending == "close-1006" else 1011 if ending == "authored-close" else None,
            close_reason=None,
            error="receive failed" if "error" in ending else None,
            error_code=None,
            transport_ended=ending == "ended-error",
        )
    )
    upstream = _SequencedUpstreamWebSocket([], deferred_message_batches=[events])
    connect = AsyncMock(return_value=(SimpleNamespace(id="only-account"), upstream))
    health = AsyncMock()
    logs = AsyncMock()
    monkeypatch.setattr(proxy_api, "_websocket_firewall_denial_response", AsyncMock(return_value=None))
    monkeypatch.setattr(proxy_api, "validate_proxy_api_key_authorization", AsyncMock(return_value=None))
    monkeypatch.setattr(
        proxy_service, "get_settings_cache", lambda: SimpleNamespace(get=AsyncMock(return_value=_websocket_settings()))
    )
    monkeypatch.setattr(proxy_service.ProxyService, "_connect_proxy_websocket", connect)
    monkeypatch.setattr(proxy_service.ProxyService, "_handle_stream_error", health)
    monkeypatch.setattr(proxy_service.ProxyService, "_write_request_log", logs)
    with TestClient(app_instance) as client:
        client.portal.call(_seed_connected_account)

        async def committed_account():
            async with SessionLocal() as session:
                return await session.get(Account, "only-account")

        connect.return_value = (client.portal.call(committed_account), upstream)
        with client.websocket_connect(path) as websocket:
            websocket.send_json(
                {"type": "response.create", "model": "gpt-5.4", "input": "hello", "instructions": "", "stream": True}
            )
            received = [json.loads(websocket.receive_text()) for _ in range(3)]
        client.portal.call(partial(get_proxy_service_for_app(app_instance).drain_persistence_tasks, timeout_seconds=5))
    terminal = received[-1]
    error = terminal["response"]["error"] if terminal["type"] == "response.failed" else terminal["error"]
    assert error["code"] == "stream_incomplete"
    assert health.await_count == int(penalized)
    assert logs.await_count == 1
    assert logs.await_args.kwargs["error_code"] == "stream_incomplete"
    assert len(upstream.sent_text) == 1
    connect.assert_awaited_once()
    assert upstream.closed


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
@pytest.mark.parametrize("frame_kind", ["error", "response.failed"])
def test_selected_owner_quota_terminal_preserves_sanitized_metadata(app_instance, monkeypatch, path, frame_kind):
    error = {
        "code": "usage_limit_reached",
        "type": "rate_limit_error",
        "message": "Quota exhausted",
        "param": "input",
        "plan_type": "plus",
        "resets_at": 1_800_000_000,
        "resets_in_seconds": 30,
    }
    frame = (
        {"type": frame_kind, "status": 429, "error": error}
        if frame_kind == "error"
        else {"type": frame_kind, "response": {"id": "resp_owner", "status": "failed", "error": error}}
    )
    events = []
    if frame_kind == "response.failed":
        events.append(
            UpstreamWebSocketMessage(
                "text", text=json.dumps({"type": "response.created", "response": {"id": "resp_owner"}})
            )
        )
    events.append(UpstreamWebSocketMessage("text", text=json.dumps(frame)))
    upstream = _SequencedUpstreamWebSocket([], deferred_message_batches=[events])
    connect = AsyncMock()
    health, logs = AsyncMock(), AsyncMock()
    monkeypatch.setattr(proxy_api, "_websocket_firewall_denial_response", AsyncMock(return_value=None))
    monkeypatch.setattr(proxy_api, "validate_proxy_api_key_authorization", AsyncMock(return_value=None))
    monkeypatch.setattr(
        proxy_service, "get_settings_cache", lambda: SimpleNamespace(get=AsyncMock(return_value=_websocket_settings()))
    )
    monkeypatch.setattr(
        proxy_service.ProxyService, "_resolve_websocket_previous_response_owner", AsyncMock(return_value="only-account")
    )
    monkeypatch.setattr(proxy_service.ProxyService, "_connect_proxy_websocket", connect)
    monkeypatch.setattr(proxy_service.ProxyService, "_handle_stream_error", health)
    monkeypatch.setattr(proxy_service.ProxyService, "_write_request_log", logs)
    with TestClient(app_instance) as client:
        client.portal.call(_seed_connected_account)

        async def committed_account():
            async with SessionLocal() as session:
                return await session.get(Account, "only-account")

        connect.return_value = (client.portal.call(committed_account), upstream)
        with client.websocket_connect(path) as websocket:
            websocket.send_json(
                {
                    "type": "response.create",
                    "model": "gpt-5.4",
                    "input": "continue",
                    "instructions": "",
                    "previous_response_id": "resp_previous",
                    "stream": True,
                }
            )
            if frame_kind == "response.failed":
                assert websocket.receive_json()["type"] == "response.created"
            terminal = websocket.receive_json()
        client.portal.call(partial(get_proxy_service_for_app(app_instance).drain_persistence_tasks, timeout_seconds=5))
    emitted = terminal["response"]["error"] if terminal["type"] == "response.failed" else terminal["error"]
    assert emitted == error
    if frame_kind == "error":
        assert terminal["status"] == 429
    assert logs.await_count == 1
    assert logs.await_args.kwargs["error_code"] == "usage_limit_reached"
    assert health.await_count == 1
    assert len(upstream.sent_text) == 1
    connect.assert_awaited_once()
