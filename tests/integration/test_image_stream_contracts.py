from __future__ import annotations

import copy
import json
import logging

import pytest
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.clients.proxy_websocket import UpstreamWebSocketMessage
from app.core.openai.models import CompactResponsePayload
from app.db.models import ApiKeyUsageReservation, RequestLog
from app.db.session import SessionLocal
from tests.integration.off_loop_test_client import off_loop_test_client
from tests.integration.test_http_responses_bridge import (
    _cleanup_http_bridge_sessions,  # noqa: F401
    _FakeBridgeUpstreamWebSocket,
    _install_bridge_settings,
)
from tests.integration.test_proxy_images import _enable_api_key_auth, _sse
from tests.integration.test_proxy_transient_retry import _create_metered_proxy_key, _import_account

pytestmark = pytest.mark.integration

IMAGE_PATHS = [
    "/v1/images/generations",
    "/backend-api/codex/images/generations",
    "/v1/images/edits",
    "/backend-api/codex/images/edits",
]


@pytest.mark.parametrize("path", IMAGE_PATHS)
@pytest.mark.parametrize("model", ["gpt-image-2.5-flare", "gpt-image-2.5-sunburst"])
@pytest.mark.parametrize("n", [1, 2])
@pytest.mark.parametrize("terminal", ["completed", "late_incomplete", "incomplete"])
async def test_image_models_fanout_terminal_and_settlement(async_client, monkeypatch, caplog, path, model, n, terminal):
    await _import_account(async_client, "image_contract_owner", "image-contract@example.com")
    await _enable_api_key_auth(async_client)
    key = await _create_metered_proxy_key(async_client, "image-contract")
    calls = []
    closed = []

    async def stream(payload, headers, access_token, account_id, **kwargs):
        index = len(calls)
        calls.append(copy.deepcopy(payload.model_dump()))
        try:
            if terminal == "incomplete":
                yield _sse({"type": "response.incomplete", "response": {"id": f"image-{index}"}})
                return
            yield _sse(
                {
                    "type": "response.completed",
                    "response": {
                        "id": f"image-{index}",
                        "status": "completed",
                        "output": [{"type": "image_generation_call", "status": "completed", "result": f"B64-{index}"}],
                        "tool_usage": {"image_gen": {"input_tokens": 7, "output_tokens": 13}},
                    },
                }
            )
            if terminal == "late_incomplete":
                yield _sse({"type": "response.incomplete", "response": {"id": f"image-{index}"}})
        finally:
            closed.append(index)

    monkeypatch.setattr(proxy_module, "core_stream_responses", stream)
    with caplog.at_level(logging.INFO, logger="app.modules.proxy.api"):
        body = {"prompt": "draw a circle", "model": model, "n": n}
        if path == "/backend-api/codex/images/edits":
            body["images"] = [{"image_url": "data:image/png;base64,iVBORw0KGgo="}]
        headers = {"Authorization": f"Bearer {key}"}
        if path == "/v1/images/edits":
            response = await async_client.post(
                path,
                headers=headers,
                data={"prompt": "draw a circle", "model": model, "n": str(n)},
                files={"image": ("source.png", b"\x89PNG\r\n\x1a\n", "image/png")},
            )
        else:
            response = await async_client.post(path, headers=headers, json=body)
    # A child may be refused during shared account admission before reaching
    # the provider. Fan-out still owns and releases one reservation.
    if terminal == "incomplete":
        assert 1 <= len(calls) <= n
    else:
        assert len(calls) == n
    assert sorted(closed) == list(range(len(calls)))
    assert all(call["tools"][0]["model"] == model for call in calls)
    assert all(call["model"] != model and "n" not in call["tools"][0] for call in calls)
    if path.endswith("edits"):
        assert all(call["tools"][0]["action"] == "edit" for call in calls)
        assert all(
            call["input"][0]["content"][1]["image_url"] == "data:image/png;base64,iVBORw0KGgo=" for call in calls
        )
    if terminal == "incomplete":
        assert response.status_code == 502, response.text
        expected_codes = {"image_generation_failed"}
        if n > 1:
            expected_codes.add("selection_state_changed")
        assert response.json()["error"]["code"] in expected_codes
    else:
        assert response.status_code == 200, response.text
        assert sorted(item["b64_json"] for item in response.json()["data"]) == [f"B64-{i}" for i in range(n)]
        assert response.json()["usage"] == {"input_tokens": 7 * n, "output_tokens": 13 * n, "total_tokens": 20 * n}
    from app.dependencies import get_proxy_service_for_app

    assert await get_proxy_service_for_app(async_client._transport.app).drain_persistence_tasks(timeout_seconds=5)
    async with SessionLocal() as session:
        reservation = (await session.execute(select(ApiKeyUsageReservation))).scalar_one()
        assert reservation.status == ("released" if terminal == "incomplete" else "finalized")
        if terminal != "incomplete":
            assert reservation.input_tokens == 7 * n
            assert reservation.output_tokens == 13 * n
    observations = [record.message for record in caplog.records if record.message.startswith("images_route_complete ")]
    assert len(observations) == 1
    assert f"model={model}" in observations[0]
    assert f"fanout={n}" in observations[0]


def _screenshot_body():
    return {
        "model": "gpt-5.1",
        "instructions": "",
        "input": [
            {"role": "user", "content": "old turn"},
            {"type": "computer_call", "call_id": "screen", "action": {"type": "screenshot"}},
            {
                "type": "computer_call_output",
                "call_id": "screen",
                "output": {"type": "computer_screenshot", "image_url": "data:image/png;base64," + "A" * 5000},
            },
            {"role": "assistant", "content": [{"type": "output_text", "text": "done"}]},
            {"role": "user", "content": "compact and continue"},
        ],
        "stream": True,
    }


def _assert_screenshot_slimmed(upstream, original):
    sent = json.loads(upstream.sent_text[0])
    assert sent["input"][-1] == original["input"][-1]
    assert sent["input"][1] == original["input"][1]
    assert sent["input"][2]["call_id"] == "screen"
    assert "data:image/" not in json.dumps(sent)
    assert "omitted historical inline image" in json.dumps(sent)


@pytest.mark.parametrize(
    "path", ["/v1/responses", "/v1/responses/", "/backend-api/codex/responses", "/backend-api/codex/responses/"]
)
async def test_hosted_screenshot_http_bridge(async_client, monkeypatch, path):
    _install_bridge_settings(monkeypatch, enabled=True)
    await _import_account(async_client, "screen_owner", "screen@example.com")
    upstream = _FakeBridgeUpstreamWebSocket("screen")

    async def connect(*args, **kwargs):
        return upstream

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    monkeypatch.setattr(proxy_module, "_UPSTREAM_RESPONSE_CREATE_MAX_BYTES", 1200)
    monkeypatch.setattr(proxy_module, "_UPSTREAM_RESPONSE_CREATE_WARN_BYTES", 1000)
    body = _screenshot_body()
    original = copy.deepcopy(body)
    response = await async_client.post(path, json=body)
    assert response.status_code == 200, response.text
    assert "response.completed" in response.text
    _assert_screenshot_slimmed(upstream, original)
    assert body == original


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_hosted_screenshot_native_websocket(async_client, app_instance, monkeypatch, path):
    await _import_account(async_client, "screen_ws_owner", "screen-ws@example.com")
    key = await _create_metered_proxy_key(async_client, "screenshot-ws")
    upstream = _FakeBridgeUpstreamWebSocket("screen_ws")

    async def connect(*args, **kwargs):
        return upstream

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    monkeypatch.setattr(proxy_module, "_UPSTREAM_RESPONSE_CREATE_MAX_BYTES", 1200)
    monkeypatch.setattr(proxy_module, "_UPSTREAM_RESPONSE_CREATE_WARN_BYTES", 1000)
    body = dict(_screenshot_body(), type="response.create")
    async with off_loop_test_client(app_instance, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        with client.websocket_connect(path, headers={"Authorization": f"Bearer {key}"}) as websocket:
            websocket.send_json(body)
            for _ in range(8):
                if websocket.receive_json()["type"] == "response.completed":
                    break
            else:
                pytest.fail("missing completion")
        _assert_screenshot_slimmed(upstream, body)


@pytest.mark.parametrize(
    "path",
    [
        "/v1/responses/compact",
        "/v1/responses/compact/",
        "/backend-api/codex/responses/compact",
        "/backend-api/codex/responses/compact/",
    ],
)
async def test_hosted_screenshot_explicit_compact_preserves_input(async_client, monkeypatch, path):
    await _import_account(async_client, "screen_compact_owner", "screen-compact@example.com")
    captured = []

    async def compact(payload, *args, **kwargs):
        captured.append(payload.model_dump())
        return CompactResponsePayload.model_validate(
            {"object": "response.compaction", "output": [{"type": "compaction", "encrypted_content": "checkpoint"}]}
        )

    monkeypatch.setattr(proxy_module, "core_compact_responses", compact)
    body = _screenshot_body()
    body.pop("stream")
    response = await async_client.post(path, json=body)
    assert response.status_code == 200, response.text
    assert captured[0]["input"] == body["input"]
    assert response.json()["output"] == [{"type": "compaction", "encrypted_content": "checkpoint"}]


class _MidTurnFailureUpstream(_FakeBridgeUpstreamWebSocket):
    error = {"code": "rate_limit_exceeded", "message": "Rate limit reached. Try again in 20s.", "type": "requests"}

    async def send_text(self, text):
        if not self.sent_text:
            await super().send_text(text)
            return
        self.sent_text.append(text)
        for event in [
            {"type": "response.created", "response": {"id": "midturn", "status": "in_progress"}},
            {"type": "response.output_text.delta", "response_id": "midturn", "delta": "partial answer"},
            {"type": "response.failed", "response": {"id": "midturn", "status": "failed", "error": self.error}},
        ]:
            await self._messages.put(UpstreamWebSocketMessage(kind="text", text=json.dumps(event)))


@pytest.mark.parametrize("path", ["/v1/responses", "/backend-api/codex/responses"])
async def test_native_midturn_failure_retains_owner_terminal(async_client, app_instance, monkeypatch, caplog, path):
    await _import_account(async_client, "midturn_owner", "midturn@example.com")
    key = await _create_metered_proxy_key(async_client, "midturn")
    upstream = _MidTurnFailureUpstream("midturn_root")
    connected = []

    async def connect(*args, **kwargs):
        connected.append(True)
        return upstream

    monkeypatch.setattr(proxy_module, "connect_responses_websocket", connect)
    async with off_loop_test_client(app_instance, base_url="http://127.0.0.1", client=("127.0.0.1", 50000)) as client:
        with client.websocket_connect(path, headers={"Authorization": f"Bearer {key}"}) as websocket:
            body = {"type": "response.create", "model": "gpt-5.1", "instructions": "", "input": "first"}
            websocket.send_json(body)
            for _ in range(8):
                first = websocket.receive_json()
                if first["type"] == "response.completed":
                    break
            else:
                pytest.fail("missing root completion")
            websocket.send_json(dict(body, input="next", previous_response_id=first["response"]["id"]))
            events = []
            for _ in range(8):
                event = websocket.receive_json()
                events.append(event)
                if event["type"] == "response.failed":
                    break
            else:
                pytest.fail("missing original failure")
            assert events[-1]["response"]["error"] == upstream.error
            assert any(event["type"] == "response.output_text.delta" for event in events)
        from app.dependencies import get_proxy_service_for_app

        assert await get_proxy_service_for_app(app_instance).drain_persistence_tasks(timeout_seconds=5)
        async with SessionLocal() as session:
            errors = (
                (await session.execute(select(RequestLog).where(RequestLog.error_code.is_not(None)))).scalars().all()
            )
            assert len(errors) == 1
            assert errors[0].error_code == "rate_limit_exceeded"
    assert len(connected) == 1
    assert len(upstream.sent_text) == 2
    assert upstream.closed
    assert "scope cleanup exceeded" not in caplog.text
