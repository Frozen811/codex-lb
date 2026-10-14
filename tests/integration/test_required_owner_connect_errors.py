from __future__ import annotations

import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

import app.modules.proxy.api as proxy_api
import app.modules.proxy.service as proxy
from app.modules.proxy.load_balancer import AccountLease, AccountSelection, LoadBalancer
from tests.integration.test_http_responses_bridge import (
    _ClosingBridgeUpstreamWebSocket,
    _get_account,
    _import_account,
    _install_bridge_settings,
)
from tests.integration.test_proxy_websocket_responses import _websocket_response_create

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
@pytest.mark.parametrize(
    "status,code", [(403, "upstream_unavailable"), (429, "usage_limit_reached"), (401, "invalid_api_key")]
)
def test_required_owner_connect_failure_retains_native_envelope(app_instance, monkeypatch, path, status, code):
    owner = SimpleNamespace(id="required-connect-owner", security_work_authorized=False)
    selections = []
    releases = []
    lease = AccountLease(account_id=owner.id, lease_id="connect-lease", kind="stream", acquired_at=0.0)
    message = f"original owner connect failure {status}"

    async def recorded_owner(self, **kwargs):
        return owner.id

    async def select_owner(self, *args, preferred_account_id=None, request_state, **kwargs):
        selections.append(preferred_account_id)
        assert len(selections) == 1, "hard owner must not be excluded and reselected"
        assert kwargs["require_preferred_account"]
        request_state.websocket_stream_lease = lease
        return owner

    async def reject_owner(self, selected, headers, **kwargs):
        assert selected.id == owner.id
        raise proxy.ProxyResponseError(status, proxy.openai_error(code, message), failure_phase="connect")

    async def classify(self, selected, exc):
        return {"failure_class": "retryable_transient"}

    async def release(self, selected_lease):
        if selected_lease is not None:
            releases.append(selected_lease)

    async def allow(*args, **kwargs):
        return None

    monkeypatch.setattr(proxy_api, "_websocket_firewall_denial_response", allow)
    monkeypatch.setattr(proxy_api, "validate_proxy_api_key_authorization", allow)
    monkeypatch.setattr(proxy.ProxyService, "_resolve_websocket_previous_response_owner", recorded_owner)
    monkeypatch.setattr(proxy.ProxyService, "_select_websocket_connect_account", select_owner)
    monkeypatch.setattr(proxy.ProxyService, "_try_open_websocket_connect_attempt", reject_owner)
    monkeypatch.setattr(proxy.ProxyService, "_handle_websocket_connect_error", classify)
    monkeypatch.setattr(LoadBalancer, "release_account_lease", release)
    request = _websocket_response_create("continue")
    request.update(model="gpt-5.5", previous_response_id="resp_required_connect_owner")
    with TestClient(app_instance) as client:
        if path.endswith("/"):
            with pytest.raises(WebSocketDisconnect) as denied:
                with client.websocket_connect(path):
                    pytest.fail("trailing-slash WebSocket routes remain unsupported")
            assert denied.value.code == 1000
            assert selections == releases == []
            return
        with client.websocket_connect(path) as socket:
            socket.send_text(json.dumps(request))
            event = json.loads(socket.receive_text())
    assert event["type"] == "error"
    assert event["status"] == status
    assert event["error"]["code"] == code
    assert event["error"]["message"] == message
    assert selections == [owner.id]
    assert releases == [lease]


@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
@pytest.mark.parametrize("status,code", [(403, "upstream_unavailable"), (429, "usage_limit_reached")])
async def test_required_owner_connect_failure_retains_http_bridge_envelope(
    async_client, monkeypatch, path, status, code
):
    _install_bridge_settings(monkeypatch, enabled=True)
    owner_id = await _import_account(async_client, "owner-connect-bridge", "owner-connect@example.com")
    owner = await _get_account(owner_id)
    selections = []
    opens = []
    first_upstream = _ClosingBridgeUpstreamWebSocket()
    message = f"original bridge owner failure {status}"

    async def select(self, deadline, **kwargs):
        selections.append(kwargs.get("preferred_account_id"))
        assert len(selections) <= 2, "a refused required owner cannot trigger replacement selection"
        if len(selections) == 2:
            assert kwargs["preferred_account_id"] == owner.id
            assert kwargs["fallback_on_preferred_account_unavailable"] is False
        return AccountSelection(account=owner, error_message=None)

    async def fresh(self, account, **kwargs):
        return account

    async def connect(headers, access_token, account_id_header, **kwargs):
        opens.append(account_id_header)
        if len(opens) == 1:
            return first_upstream
        raise proxy.ProxyResponseError(status, proxy.openai_error(code, message), failure_phase="connect")

    monkeypatch.setattr(proxy.ProxyService, "_select_account_with_budget", select)
    monkeypatch.setattr(proxy.ProxyService, "_ensure_fresh_with_budget", fresh)
    monkeypatch.setattr(proxy, "connect_responses_websocket", connect)
    body = {"model": "gpt-5.1", "input": "hello", "instructions": "Return OK", "prompt_cache_key": "owner-connect-key"}
    first = await async_client.post(path, json=body)
    assert first.status_code == 200, first.text
    if first.headers["content-type"].startswith("text/event-stream"):
        events = [json.loads(line[6:]) for line in first.text.splitlines() if line.startswith("data: {")]
        response_id = next(event["response"]["id"] for event in events if event["type"] == "response.completed")
    else:
        response_id = first.json()["id"]
    body.update(input="continue", previous_response_id=response_id)
    second = await async_client.post(path, json=body)
    assert second.status_code == status, second.text
    assert second.json()["error"]["code"] == code
    assert second.json()["error"]["message"] == message
    assert selections == [None, owner.id]
    assert len(opens) == 2
