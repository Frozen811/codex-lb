from __future__ import annotations

import pytest

from app.core.openai.requests import ResponsesRequest
from app.core.types import JsonValue
from app.modules.proxy._service.http_bridge.helpers import _http_bridge_payload_looks_like_full_resend
from app.modules.proxy.http_bridge_forwarding import (
    HTTPBridgeForwardContext,
    build_owner_forward_headers,
    parse_forwarded_request,
)
from app.modules.proxy.replay_safety import responses_input_items_are_self_contained_fresh_replay


@pytest.mark.parametrize("call_type", ["function_call", "custom_tool_call"])
def test_async_pending_call_allows_intervening_completed_assistant(call_type: str) -> None:
    call: dict[str, JsonValue] = {"type": call_type, "call_id": "async_one", "name": "slow", "async": True}
    call["arguments" if call_type == "function_call" else "input"] = "{}"
    items: list[JsonValue] = [
        call,
        {"role": "assistant", "content": [{"type": "output_text", "text": "Working"}], "status": "completed"},
        {"role": "user", "content": [{"type": "input_text", "text": "Continue"}]},
    ]
    assert responses_input_items_are_self_contained_fresh_replay(items)


@pytest.mark.parametrize(
    "input_value",
    [
        "x" * 4095,
        "x" * 4096,
        [{"type": "function_call_output", "call_id": "a", "output": "x" * 8192}],
        [
            {"type": "function_call_output", "call_id": "a", "output": "ready"},
            {"type": "custom_tool_call_output", "call_id": "b", "output": "ready"},
        ],
    ],
    ids=["short-string", "long-string", "large-output", "parallel-outputs"],
)
def test_delta_classification_survives_signed_owner_roundtrip(
    input_value: JsonValue, monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    from app.core.config.settings import get_settings

    monkeypatch.setenv("CODEX_LB_ENCRYPTION_KEY_FILE", str(tmp_path / "bridge.key"))
    get_settings.cache_clear()
    try:
        payload = ResponsesRequest.model_validate({"model": "gpt-6-astra", "instructions": "", "input": input_value})
        context = HTTPBridgeForwardContext(
            origin_instance="origin", target_instance="owner", codex_session_affinity=True, downstream_turn_state="turn"
        )
        headers = build_owner_forward_headers(headers={}, payload=payload, context=context)
        received = ResponsesRequest.model_validate(payload.model_dump_for_forwarding())
        forwarded, error = parse_forwarded_request(headers, payload=received, current_instance="owner")
        assert error is None
        assert forwarded is not None
        assert not _http_bridge_payload_looks_like_full_resend(payload)
        assert not _http_bridge_payload_looks_like_full_resend(received)
    finally:
        get_settings.cache_clear()
