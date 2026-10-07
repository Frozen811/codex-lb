from __future__ import annotations

import json

import pytest

from app.core.errors import (
    PREVIOUS_RESPONSE_STREAM_INCOMPLETE_MESSAGE,
    OpenAIErrorParam,
    is_previous_response_not_found_error,
    is_previous_response_not_found_public_shape,
    previous_response_id_from_not_found_message,
    previous_response_stream_incomplete_error,
    response_failed_event,
)
from app.core.openai.models import OpenAIError
from app.core.types import JsonValue
from app.modules.proxy._service.streaming.retry import _response_failed_event_from_upstream_error
from app.modules.proxy._service.websocket.helpers import _websocket_event_upstream_error
from app.modules.proxy.helpers import _parse_openai_error, _upstream_error_from_openai


@pytest.mark.parametrize("reset", [True, False, "bad", float("nan"), float("inf"), float("-inf")])
def test_quota_terminal_ignores_malformed_reset_metadata(reset: JsonValue) -> None:
    event = _response_failed_event_from_upstream_error(
        "usage_limit_reached", {"message": "limit reached", "resets_at": reset}
    )

    assert event["response"]["error"] == {
        "code": "usage_limit_reached",
        "message": "limit reached",
        "type": "server_error",
    }
    json.dumps(event, allow_nan=False)


@pytest.mark.parametrize("field", ["resets_at", "resets_in_seconds"])
@pytest.mark.parametrize("reset", [True, "bad", float("nan"), float("inf"), float("-inf"), "NaN", "Infinity"])
def test_upstream_quota_parser_validates_reset_fields_independently(field: str, reset: JsonValue) -> None:
    valid_field = "resets_in_seconds" if field == "resets_at" else "resets_at"
    valid_reset = 432_000 if valid_field == "resets_in_seconds" else 2_000_432_000
    error = {"code": "usage_limit_reached", "message": "limit reached", field: reset, valid_field: valid_reset}

    parsed = _parse_openai_error({"error": error})
    assert parsed is not None
    assert parsed.code == "usage_limit_reached"
    assert parsed.message == "limit reached"
    assert _upstream_error_from_openai(parsed) == {"message": "limit reached", valid_field: valid_reset}
    assert _websocket_event_upstream_error("error", {"type": "error", "error": error}) == {
        "message": "limit reached",
        valid_field: valid_reset,
    }


@pytest.mark.parametrize("reset", [2_000_432_000, 2_000_432_000.5, "2000432000.5"])
def test_upstream_quota_parser_preserves_finite_reset_compatibility(reset: int | float | str) -> None:
    parsed = _parse_openai_error({"error": {"message": "limit reached", "resets_at": reset}})
    assert parsed is not None
    expected = float(reset) if isinstance(reset, str) else reset
    assert parsed.resets_at == expected
    event = _response_failed_event_from_upstream_error("usage_limit_reached", _upstream_error_from_openai(parsed))
    assert event["response"]["error"]["resets_at"] == int(expected)
    assert "resets_in_seconds" not in event["response"]["error"]


@pytest.mark.parametrize("reset", [float("nan"), float("inf"), float("-inf")])
def test_typed_upstream_error_ignores_nonfinite_resets(reset: float) -> None:
    parsed = OpenAIError(message="limit reached", resets_at=reset, resets_in_seconds=432_000)
    assert parsed.resets_at is None
    assert parsed.resets_in_seconds == 432_000


def test_response_failed_event_includes_incomplete_details():
    event = response_failed_event("stream_incomplete", "Upstream closed stream", response_id="resp_1")

    response = event["response"]
    assert "incomplete_details" in response
    assert response["incomplete_details"] is None


def test_response_failed_event_accepts_incomplete_details():
    event = response_failed_event(
        "stream_incomplete",
        "Upstream closed stream",
        response_id="resp_1",
        incomplete_details={"reason": "max_output_tokens"},
    )

    response = event["response"]
    assert response.get("incomplete_details") == {"reason": "max_output_tokens"}


def test_response_failed_event_preserves_reset_hint():
    event = response_failed_event(
        "usage_limit_reached",
        "Rate limit exceeded. Try again in 1h",
        error_type="usage_limit_reached",
        response_id="resp_1",
        resets_at=1_700_003_600,
    )

    assert event["response"]["error"].get("resets_at") == 1_700_003_600


def test_previous_response_not_found_classifier_covers_openai_shapes():
    assert is_previous_response_not_found_error(
        code="previous_response_not_found",
        param=None,
        message="Previous response with id 'resp_abc' not found.",
    )
    assert is_previous_response_not_found_error(
        code="invalid_request_error",
        param="previous_response_id",
        message='Previous response with id "resp_abc" not found.',
    )
    assert is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="Invalid `previous_response_id`.",
    )
    assert is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="Invalid `previous_response_id`",
    )
    assert is_previous_response_not_found_error(
        code="invalid_request_error",
        param="previous_response_id",
        message="Invalid `previous_response_id`.",
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param="input",
        message='Previous response with id "resp_abc" not found.',
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param="input",
        message="Invalid `previous_response_id`.",
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="Invalid request payload.",
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="Invalid `previous_response_id`...",
    )
    assert not is_previous_response_not_found_error(
        code=None,
        param=None,
        message="Invalid `previous_response_id`.",
    )


def test_previous_response_not_found_classifier_covers_parameterless_invalid_anchor():
    assert is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="Invalid `previous_response_id`.",
    )
    assert is_previous_response_not_found_error(
        code="invalid_request_error",
        param="previous_response_id",
        message="Invalid previous_response_id.",
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param="input",
        message="Invalid previous_response_id.",
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="Invalid input.",
    )
    assert not is_previous_response_not_found_error(
        code="invalid_request_error",
        param=None,
        message="A required tool output from the previous response was not found.",
    )


def test_previous_response_not_found_classifier_rejects_non_string_param():
    for param in (0, False, {}, []):
        assert not is_previous_response_not_found_error(
            code="invalid_request_error",
            param=param,
            message="Invalid previous_response_id.",
        )


def test_error_param_retains_presence_and_normalizes_public_strings():
    absent = OpenAIErrorParam.absent()
    assert not absent.present
    assert absent.raw is None
    assert absent.normalized is None
    assert not absent.malformed

    valid = OpenAIErrorParam(True, " previous_response_id ")
    assert valid.present
    assert valid.normalized == "previous_response_id"
    assert not valid.malformed

    for raw in (None, 0, False, {}, [], "", "   "):
        malformed = OpenAIErrorParam(True, raw)
        assert malformed.present
        assert malformed.malformed


def test_previous_response_not_found_classifier_fails_closed_for_malformed_present_param():
    message = "Invalid `previous_response_id`."
    for param in (OpenAIErrorParam(True, None), OpenAIErrorParam(True, 0), OpenAIErrorParam(True, " ")):
        assert not is_previous_response_not_found_error(
            code="invalid_request_error",
            param=param,
            message=message,
        )


def test_previous_response_not_found_public_shape_masks_malformed_stale_id_message():
    assert is_previous_response_not_found_public_shape(
        code="invalid_request_error",
        param=OpenAIErrorParam(True, None),
        message="Previous response with id 'resp_abc' not found.",
    )
    assert not is_previous_response_not_found_public_shape(
        code="invalid_request_error",
        param=OpenAIErrorParam(True, "input"),
        message="Previous response with id 'resp_abc' not found.",
    )
    assert not is_previous_response_not_found_public_shape(
        code="invalid_request_error",
        param=OpenAIErrorParam.absent(),
        message="A required tool output from the previous response was not found.",
    )


def test_response_failed_event_omits_malformed_param_and_trims_valid_param():
    malformed = response_failed_event(
        "stream_incomplete",
        "closed",
        error_param=OpenAIErrorParam(True, None),
    )
    assert "param" not in malformed["response"]["error"]

    valid = response_failed_event(
        "stream_incomplete",
        "closed",
        error_param=OpenAIErrorParam(True, " model "),
    )
    assert valid["response"]["error"].get("param") == "model"


def test_previous_response_id_from_not_found_message_extracts_anchor():
    assert (
        previous_response_id_from_not_found_message(
            'Previous response with id "resp_0ba42212936dca97016a0d52aec2588191bc2499d3088e4e3e" not found.'
        )
        == "resp_0ba42212936dca97016a0d52aec2588191bc2499d3088e4e3e"
    )


def test_previous_response_stream_incomplete_error_is_public_safe():
    payload = previous_response_stream_incomplete_error()

    assert payload["error"].get("code") == "stream_incomplete"
    assert payload["error"].get("type") == "server_error"
    assert payload["error"].get("message") == PREVIOUS_RESPONSE_STREAM_INCOMPLETE_MESSAGE
