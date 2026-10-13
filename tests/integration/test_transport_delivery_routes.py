from __future__ import annotations

import json
from collections import deque
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import app.modules.proxy.service as proxy_module
from app.core.balancer.logic import _format_retry_hint
from app.core.clients.proxy_websocket import UpstreamWebSocketMessage
from app.dependencies import get_proxy_service_for_app
from app.modules.proxy import api as proxy_api_module
from app.modules.proxy._service.http_bridge import queues, streaming
from app.modules.proxy.load_balancer import AccountSelection
from tests.integration.test_http_responses_bridge import (
    _FakeBridgeUpstreamWebSocket,
    _get_account,
    _import_account,
    _install_bridge_settings,
)

pytestmark = pytest.mark.integration


class _BudgetOverflowUpstream(_FakeBridgeUpstreamWebSocket):
    def __init__(self) -> None:
        super().__init__("resp_budget")
        self._injected: deque[UpstreamWebSocketMessage] = deque()
        self._overflow_sent = False

    async def receive(self) -> UpstreamWebSocketMessage:
        if self._injected:
            return self._injected.popleft()
        message = await super().receive()
        payload = json.loads(message.text or "{}")
        if payload.get("type") == "response.completed" and not self._overflow_sent:
            self._overflow_sent = True
            response_id = payload["response"]["id"]
            for delta in ("prefix", "x" * 6000):
                self._injected.append(
                    UpstreamWebSocketMessage(
                        "text",
                        text=json.dumps(
                            {"type": "response.output_text.delta", "response_id": response_id, "delta": delta}
                        ),
                    )
                )
            self._injected.append(message)
            return self._injected.popleft()
        return message


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("path", "native"),
    [("/v1/responses", False), ("/backend-api/codex/responses", False), ("/backend-api/codex/responses", True)],
)
async def test_budget_overflow_returns_ordered_sse_then_allows_same_session_turn(
    async_client, app_instance, monkeypatch, path, native
):
    _install_bridge_settings(monkeypatch, enabled=True)
    monkeypatch.setattr(queues, "_HTTP_BRIDGE_STREAM_PROCESS_BYTES_LIMIT", 2048)
    account_id = await _import_account(async_client, "acc_delivery_budget", "budget@example.com")
    account = await _get_account(account_id)
    upstream = _BudgetOverflowUpstream()
    service = get_proxy_service_for_app(app_instance)
    monkeypatch.setattr(
        service,
        "_select_account_with_budget",
        AsyncMock(return_value=AccountSelection(account=account, error_message=None, error_code=None)),
    )
    monkeypatch.setattr(service, "_ensure_fresh_with_budget", AsyncMock(return_value=account))
    monkeypatch.setattr(proxy_module, "connect_responses_websocket", AsyncMock(return_value=upstream))
    health_error = AsyncMock()
    monkeypatch.setattr(service._load_balancer, "record_error", health_error)
    body = {"model": "gpt-5.1", "instructions": "Return OK", "input": "hello", "stream": True}
    headers = {"session_id": "budget-session"}
    if native:
        headers["originator"] = "codex_cli_rs"
    try:
        first = await async_client.post(path, json=body, headers=headers)
        assert first.status_code == 200, first.text
        events = [
            json.loads(line[6:])
            for line in first.text.splitlines()
            if line.startswith("data: ") and line[6:] != "[DONE]"
        ]
        events = [event for event in events if event["type"] != "codex.keepalive"]
        assert [event["type"] for event in events] == [
            "response.created",
            "response.output_text.delta",
            "response.failed",
        ]
        assert events[1]["delta"] == "prefix"
        assert events[-1]["response"]["error"]["code"] == "stream_incomplete"
        assert "x" * 6000 not in first.text
        second = await async_client.post(path, json=body, headers=headers)
        assert second.status_code == 200 and "response.completed" in second.text, second.text
        assert len(upstream.sent_text) == 2
        assert not upstream.closed
        health_error.assert_not_awaited()
    finally:
        await service.close_all_http_bridge_sessions()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
@pytest.mark.parametrize("wait", [30, 300])
async def test_selector_generated_hint_is_terminal_at_http_routes(async_client, monkeypatch, path, wait):
    _install_bridge_settings(monkeypatch, enabled=True)
    select = AsyncMock(
        return_value=AccountSelection(account=None, error_message=_format_retry_hint(wait), error_code="no_accounts")
    )
    monkeypatch.setattr(proxy_module.ProxyService, "_select_account_with_budget", select)

    def unexpected_wait(**kwargs):
        raise AssertionError(f"Local selector hint entered capacity wait: {kwargs}")

    monkeypatch.setattr(streaming, "_iter_account_capacity_wait_sse", unexpected_wait)
    response = await async_client.post(
        path, json={"model": "gpt-5.1", "instructions": "Return OK", "input": "hello", "stream": True}
    )
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "no_accounts"
    assert "waiting_for_account_capacity" not in response.text
    select.assert_awaited_once()


@pytest.mark.parametrize("path", ["/backend-api/codex/responses", "/backend-api/codex/responses/"])
@pytest.mark.parametrize("wait", [30, 300])
def test_selector_generated_hint_is_terminal_at_websocket_route(app_instance, monkeypatch, path, wait):
    _install_bridge_settings(monkeypatch, enabled=True)
    monkeypatch.setattr(proxy_api_module, "_websocket_firewall_denial_response", AsyncMock(return_value=None))
    monkeypatch.setattr(proxy_api_module, "validate_proxy_api_key_authorization", AsyncMock(return_value=None))
    select = AsyncMock(
        return_value=AccountSelection(account=None, error_message=_format_retry_hint(wait), error_code="no_accounts")
    )
    monkeypatch.setattr(proxy_module.ProxyService, "_select_account_with_budget", select)
    with TestClient(app_instance) as client:
        if path.endswith("/"):
            # This existing WS alias is unregistered; HTTP slash aliases above
            # are registered and exercise selection. Preserve that boundary.
            with pytest.raises(WebSocketDisconnect) as rejected:
                with client.websocket_connect(path):
                    pytest.fail("Unregistered WS slash alias unexpectedly accepted")
            assert rejected.value.code == 1000
            select.assert_not_awaited()
            return
        with client.websocket_connect(path) as websocket:
            websocket.send_json(
                {"type": "response.create", "model": "gpt-5.1", "instructions": "Return OK", "input": "hello"}
            )
            event = websocket.receive_json()
    assert event["type"] == "error"
    assert event["status"] == 503
    assert event["error"]["code"] == "no_accounts"
    select.assert_awaited_once()
