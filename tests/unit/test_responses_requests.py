from __future__ import annotations

import pytest

from app.core.openai.chat_requests import ChatCompletionsRequest
from app.core.openai.requests import ResponsesCompactRequest, ResponsesRequest
from app.core.openai.v1_requests import V1ResponsesCompactRequest, V1ResponsesRequest

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("parallel_tool_calls", [True, False, None])
def test_responses_requests_never_forward_parallel_tool_calls_in_upstream_payload(
    parallel_tool_calls: bool | None,
) -> None:
    """Issue #2465: upstream Responses API / Responses-Lite HTTP path does not support

    ``parallel_tool_calls``; it must always be stripped by ``to_payload()`` even
    when explicitly provided.
    """
    data = {
        "model": "gpt-5.6",
        "instructions": "You are a helpful assistant.",
        "input": "hello",
        "tools": [{"type": "function", "name": "get_weather", "parameters": {"type": "object"}}],
        "tool_choice": "auto",
    }
    if parallel_tool_calls is not None:
        data["parallel_tool_calls"] = parallel_tool_calls

    req = ResponsesRequest.model_validate(data)
    payload = req.to_payload()

    assert "parallel_tool_calls" not in payload
    assert payload["tools"] == [{"type": "function", "name": "get_weather", "parameters": {"type": "object"}}]
    assert payload["tool_choice"] == "auto"

    replay_payload = req.to_replay_safety_payload()
    assert "parallel_tool_calls" not in replay_payload


def test_responses_requests_image_plus_tools_strips_parallel_tool_calls() -> None:
    """Issue #2465 part 2: requests containing an input image plus tools bypass the bridge,

    reach the Responses-Lite HTTP path, and must not contain ``parallel_tool_calls``.
    """
    req = ResponsesRequest.model_validate(
        {
            "model": "gpt-5.6",
            "instructions": "Analyze this image and run tools as needed.",
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": "What is in this diagram?"},
                        {"type": "input_image", "image_url": "data:image/png;base64,AAAA", "detail": "auto"},
                    ],
                }
            ],
            "tools": [{"type": "function", "name": "search_docs", "parameters": {"type": "object"}}],
            "tool_choice": "auto",
            "parallel_tool_calls": True,
        }
    )

    upstream_wire = req.to_payload()
    assert "parallel_tool_calls" not in upstream_wire
    assert len(upstream_wire["tools"]) == 1
    assert upstream_wire["tools"][0]["name"] == "search_docs"
    assert upstream_wire["tool_choice"] == "auto"

    # Input items preserved
    user_item = upstream_wire["input"][0]
    assert user_item["role"] == "user"
    assert len(user_item["content"]) == 2
    assert user_item["content"][1]["type"] == "input_image"


@pytest.mark.parametrize("parallel_tool_calls", [True, False])
def test_v1_responses_requests_converts_and_strips_parallel_tool_calls(parallel_tool_calls: bool) -> None:
    v1_req = V1ResponsesRequest.model_validate(
        {
            "model": "gpt-5.6",
            "instructions": "Be terse.",
            "input": "hi",
            "parallel_tool_calls": parallel_tool_calls,
        }
    )
    responses_req = v1_req.to_responses_request()
    payload = responses_req.to_payload()
    assert "parallel_tool_calls" not in payload


@pytest.mark.parametrize("parallel_tool_calls", [True, False])
def test_chat_completions_converts_to_responses_and_strips_parallel_tool_calls(
    parallel_tool_calls: bool,
) -> None:
    chat_req = ChatCompletionsRequest.model_validate(
        {
            "model": "gpt-5.6",
            "messages": [{"role": "user", "content": "hi"}],
            "parallel_tool_calls": parallel_tool_calls,
            "tools": [
                {
                    "type": "function",
                    "function": {"name": "test_func", "parameters": {"type": "object"}},
                }
            ],
        }
    )
    responses_req = chat_req.to_responses_request()
    payload = responses_req.to_payload()
    assert "parallel_tool_calls" not in payload
    assert len(payload["tools"]) == 1


@pytest.mark.parametrize("parallel_tool_calls", [True, False])
def test_compact_requests_strips_parallel_tool_calls(parallel_tool_calls: bool) -> None:
    compact_req = ResponsesCompactRequest.model_validate(
        {
            "model": "gpt-5.1",
            "instructions": "hi",
            "input": [],
            "parallel_tool_calls": parallel_tool_calls,
        }
    )
    payload = compact_req.to_payload()
    assert "parallel_tool_calls" not in payload


@pytest.mark.parametrize("parallel_tool_calls", [True, False])
def test_v1_compact_requests_strips_parallel_tool_calls(parallel_tool_calls: bool) -> None:
    v1_compact = V1ResponsesCompactRequest.model_validate(
        {
            "model": "gpt-5.1",
            "instructions": "hi",
            "input": [],
            "parallel_tool_calls": parallel_tool_calls,
        }
    )
    compact_req = v1_compact.to_compact_request()
    payload = compact_req.to_payload()
    assert "parallel_tool_calls" not in payload
