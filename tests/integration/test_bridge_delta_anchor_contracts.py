from __future__ import annotations

import json

import pytest

from app.core.types import JsonValue
from app.modules.proxy import service as proxy_module
from app.modules.proxy.load_balancer import AccountSelection
from tests.integration.test_http_responses_bridge import (
    _FakeBridgeUpstreamWebSocket,
    _get_account,
    _import_account,
    _install_bridge_settings,
)

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
@pytest.mark.parametrize(
    "delta",
    [
        pytest.param("x" * 4095, id="short-string"),
        pytest.param("x" * 4096, id="long-string"),
        pytest.param([{"type": "function_call_output", "call_id": "call_a", "output": "x" * 8192}], id="large-output"),
        pytest.param(
            [
                {"type": "function_call_output", "call_id": "call_a", "output": "ready"},
                {"type": "custom_tool_call_output", "call_id": "call_b", "output": "ready"},
            ],
            id="parallel-outputs",
        ),
    ],
)
async def test_public_bridge_delta_preserves_previous_response_anchor(
    async_client, monkeypatch: pytest.MonkeyPatch, path: str, delta: JsonValue
) -> None:
    _install_bridge_settings(monkeypatch, enabled=True)
    account_id = await _import_account(async_client, "delta-owner", "delta-owner@example.com")
    account = await _get_account(account_id)
    upstream = _FakeBridgeUpstreamWebSocket()
    connected: list[str] = []

    async def select_account(*args, **kwargs):
        return AccountSelection(account=account, error_message=None, error_code=None)

    async def fresh(self, target, **kwargs):
        return target

    async def connect(*args, **kwargs):
        connected.append(account.id)
        return upstream

    monkeypatch.setattr(proxy_module.ProxyService, "_select_account_with_budget", select_account)
    monkeypatch.setattr(proxy_module.ProxyService, "_ensure_fresh_with_budget", fresh)
    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    base = {"model": "gpt-6-astra", "instructions": "", "prompt_cache_key": "delta-anchor", "stream": True}
    first = await async_client.post(path, json={**base, "input": "Begin"}, follow_redirects=False)
    assert first.status_code == 200, first.text
    second = await async_client.post(
        path, json={**base, "previous_response_id": "resp_bridge_1", "input": delta}, follow_redirects=False
    )
    assert second.status_code == 200, second.text
    assert "response.completed" in second.text
    assert connected == [account.id]
    assert len(upstream.sent_text) == 2
    sent = json.loads(upstream.sent_text[1])
    assert sent["previous_response_id"] == "resp_bridge_1"
    if isinstance(delta, list):
        assert sent["input"] == delta
    else:
        assert sent["input"] == [{"role": "user", "content": [{"type": "input_text", "text": delta}]}]
