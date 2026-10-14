from __future__ import annotations

import copy
import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.core.openai.requests import ResponsesRequest
from app.modules.proxy import service as facade
from app.modules.proxy._service.streaming import helpers
from app.modules.proxy.images_service import collect_responses_stream_for_images

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("trailing", ["response.incomplete", "response.failed", "error", "response.completed"])
async def test_completed_image_is_stable_while_stream_drains(trailing):
    done = []
    original = {
        "id": "first",
        "output": [{"type": "image_generation_call", "status": "completed", "result": "ORIGINAL"}],
        "tool_usage": {"image_gen": {"input_tokens": 7, "output_tokens": 13}},
    }

    async def stream():
        yield "data: " + json.dumps({"type": "response.completed", "response": copy.deepcopy(original)}) + "\n\n"
        yield (
            "data: "
            + json.dumps(
                {
                    "type": trailing,
                    "response": {
                        "id": "second",
                        "output": [],
                        "tool_usage": {"image_gen": {"input_tokens": 999, "output_tokens": 999}},
                    },
                }
            )
            + "\n\n"
        )
        done.append(True)

    captured = {}
    result, error = await collect_responses_stream_for_images(stream(), captured=captured)
    assert error is None
    assert result == original
    assert captured == {"response_id": "first", "image_input_tokens": 7, "image_output_tokens": 13}
    assert done == [True]


@pytest.mark.parametrize("explicit", [False, True])
async def test_extracted_stream_entrypoint_preserves_lazy_retry_and_options(monkeypatch, explicit):
    started = []

    async def retry(payload, headers, **options):
        started.append((payload, headers, options))
        yield "event"

    proxy = SimpleNamespace(_stream_with_retry=retry)
    payload = ResponsesRequest.model_validate({"model": "gpt-5.1", "instructions": "", "input": "hello"})
    before = payload.model_dump()
    log = Mock()
    monkeypatch.setattr(helpers, "_maybe_log_proxy_request_payload", log)
    options = (
        {
            "codex_session_affinity": True,
            "propagate_http_errors": True,
            "openai_cache_affinity": True,
            "suppress_text_done_events": True,
            "request_transport": "websocket",
            "client_ip": "127.0.0.9",
            "enforce_openai_sdk_contract": False,
        }
        if explicit
        else {}
    )
    assert facade.ProxyService.stream_responses is helpers._stream_responses
    stream = helpers._stream_responses(
        proxy, payload, {"Authorization": "secret", "chatgpt-account-id": "private", "session_id": "session"}, **options
    )
    assert started == []
    log.assert_called_once()
    assert [event async for event in stream] == ["event"]
    forwarded_payload, headers, forwarded = started[0]
    assert forwarded_payload is payload
    assert payload.model_dump() == before
    assert "authorization" not in {key.lower() for key in headers}
    assert "chatgpt-account-id" not in {key.lower() for key in headers}
    assert headers["session_id"] == "session"
    assert forwarded["api_key"] is None and forwarded["api_key_reservation"] is None
    for name, value in options.items():
        assert forwarded[name] == value
    if not explicit:
        assert forwarded["request_transport"] == "http"
        assert forwarded["enforce_openai_sdk_contract"] is True
        assert forwarded["propagate_http_errors"] is False
