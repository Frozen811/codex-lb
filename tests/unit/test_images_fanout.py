from __future__ import annotations

import asyncio
import json
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from app.core.clock import REAL_SCHEDULER
from app.core.openai.requests import ResponsesRequest
from app.modules.proxy.images_fanout import execute_image_fanout

pytestmark = pytest.mark.unit


def _make_mock_request():
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/v1/images/generations",
        "headers": [(b"content-type", b"application/json")],
    }
    return Request(scope)


@pytest.mark.asyncio
async def test_execute_image_fanout_success():
    mock_context = MagicMock()
    mock_context.service._scheduler = REAL_SCHEDULER
    mock_context.service.rewrite_request_log_model = AsyncMock()

    mock_request = _make_mock_request()
    payload = ResponsesRequest(
        model="gpt-4o",
        input=[{"type": "message", "role": "user", "content": "draw cats"}],
        instructions="generate image",
    )

    mock_reservation = MagicMock()

    # Helpers
    async def mock_prime(req, upstream, headers, on_error=None):
        return upstream, None

    def mock_logged_error(req, status, envelope, headers=None):
        return JSONResponse(status_code=status, content=envelope, headers=headers)

    def mock_status_for_err(env):
        return 400

    mock_release = AsyncMock()
    mock_finalize = AsyncMock()

    def mock_client_host(req):
        return "127.0.0.1"

    # Mock collect and response
    call_idx = 0

    async def mock_collect(upstream: Any, *, captured: Any = None) -> Any:
        nonlocal call_idx
        call_idx += 1
        if captured is not None:
            captured["image_input_tokens"] = 100
            captured["image_output_tokens"] = 50
            captured["image_cached_input_tokens"] = 20
            captured["response_id"] = f"resp-{call_idx}"
        return (
            {
                "output": [
                    {
                        "type": "image_generation_call",
                        "status": "completed",
                        "result": f"base64_data_{call_idx}",
                    }
                ]
            },
            None,
        )

    # Monkeypatch collect_responses_stream_for_images in images_fanout's imported module
    import app.modules.proxy.images_service as svc

    orig_collect = svc.collect_responses_stream_for_images
    setattr(svc, "collect_responses_stream_for_images", mock_collect)
    try:
        resp = await execute_image_fanout(
            context=mock_context,
            request=mock_request,
            responses_payload=payload,
            api_key=None,
            reservation=mock_reservation,
            rate_limit_headers={"x-ratelimit-remaining": "10"},
            public_model="gpt-image-2",
            route="generations",
            n=3,
            started_at=1000.0,
            prime_upstream_stream=mock_prime,
            logged_error_json_response=mock_logged_error,
            status_for_image_error_envelope=mock_status_for_err,
            release_reservation=mock_release,
            finalize_image_reservation=mock_finalize,
            resolve_client_host=mock_client_host,
        )
    finally:
        setattr(svc, "collect_responses_stream_for_images", orig_collect)

    assert resp.status_code == 200
    body = json.loads(bytes(resp.body))
    assert len(body["data"]) == 3
    assert body["data"][0]["b64_json"] == "base64_data_1"
    assert body["data"][1]["b64_json"] == "base64_data_2"
    assert body["data"][2]["b64_json"] == "base64_data_3"

    # Aggregated tokens
    assert body["usage"]["input_tokens"] == 300
    assert body["usage"]["output_tokens"] == 150
    assert body["usage"]["total_tokens"] == 450
    assert body["usage"]["input_tokens_details"]["cached_tokens"] == 60

    # Finalize called with total sum
    mock_finalize.assert_awaited_once_with(
        mock_context.service,
        None,
        mock_reservation,
        model="gpt-image-2",
        input_tokens=300,
        output_tokens=150,
        cached_input_tokens=60,
    )
    # Model rewrite called for all 3 response IDs
    assert mock_context.service.rewrite_request_log_model.await_count == 3


@pytest.mark.asyncio
async def test_execute_image_fanout_error_handling():
    mock_context = MagicMock()
    mock_context.service._scheduler = REAL_SCHEDULER
    mock_request = _make_mock_request()
    payload = ResponsesRequest(
        model="gpt-4o",
        input=[{"type": "message", "role": "user", "content": "draw"}],
        instructions="gen",
    )
    mock_reservation = MagicMock()

    async def mock_prime(req, upstream, headers, on_error=None):
        return None, JSONResponse(status_code=502, content={"error": {"message": "bad gateway"}})

    def mock_logged_error(req, status, envelope, headers=None):
        return JSONResponse(status_code=status, content=envelope, headers=headers)

    mock_release = AsyncMock()
    mock_finalize = AsyncMock()

    resp = await execute_image_fanout(
        context=mock_context,
        request=mock_request,
        responses_payload=payload,
        api_key=None,
        reservation=mock_reservation,
        rate_limit_headers={},
        public_model="gpt-image-2",
        route="generations",
        n=2,
        started_at=1000.0,
        prime_upstream_stream=mock_prime,
        logged_error_json_response=mock_logged_error,
        status_for_image_error_envelope=lambda e: 500,
        release_reservation=mock_release,
        finalize_image_reservation=mock_finalize,
        resolve_client_host=lambda r: "127.0.0.1",
    )

    assert resp.status_code == 502
    mock_release.assert_awaited_once_with(mock_reservation)
    mock_finalize.assert_not_called()


@pytest.mark.asyncio
async def test_execute_image_fanout_partial_failure_settles_usage():
    mock_context = MagicMock()
    mock_context.service._scheduler = REAL_SCHEDULER
    mock_context.service.rewrite_request_log_model = AsyncMock()
    mock_request = _make_mock_request()
    payload = ResponsesRequest(
        model="gpt-4o",
        input=[{"type": "message", "role": "user", "content": "draw"}],
        instructions="gen",
    )
    mock_reservation = MagicMock()

    call_count = 0

    async def mock_prime(req, upstream, headers, on_error=None):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return upstream, None
        return None, JSONResponse(status_code=500, content={"error": {"message": "subcall 2 failed"}})

    def mock_logged_error(req, status, envelope, headers=None):
        return JSONResponse(status_code=status, content=envelope, headers=headers)

    mock_release = AsyncMock()
    mock_finalize = AsyncMock()

    async def mock_collect(upstream: Any, *, captured: Any = None) -> Any:
        if captured is not None:
            captured["image_input_tokens"] = 120
            captured["image_output_tokens"] = 60
            captured["image_cached_input_tokens"] = 10
            captured["response_id"] = "resp-subcall-1"
        return (
            {
                "output": [
                    {
                        "type": "image_generation_call",
                        "status": "completed",
                        "result": "base64_data_partial",
                    }
                ]
            },
            None,
        )

    import app.modules.proxy.images_service as svc

    orig_collect = svc.collect_responses_stream_for_images
    setattr(svc, "collect_responses_stream_for_images", mock_collect)
    try:
        resp = await execute_image_fanout(
            context=mock_context,
            request=mock_request,
            responses_payload=payload,
            api_key=None,
            reservation=mock_reservation,
            rate_limit_headers={},
            public_model="gpt-image-2",
            route="generations",
            n=2,
            started_at=1000.0,
            prime_upstream_stream=mock_prime,
            logged_error_json_response=mock_logged_error,
            status_for_image_error_envelope=lambda e: 500,
            release_reservation=mock_release,
            finalize_image_reservation=mock_finalize,
            resolve_client_host=lambda r: "127.0.0.1",
        )
    finally:
        setattr(svc, "collect_responses_stream_for_images", orig_collect)

    # First error is surfaced
    assert resp.status_code == 500
    # Successful subcall usage is settled!
    mock_finalize.assert_awaited_once_with(
        mock_context.service,
        None,
        mock_reservation,
        model="gpt-image-2",
        input_tokens=120,
        output_tokens=60,
        cached_input_tokens=10,
    )
    # Release is NOT called because usage was finalized
    mock_release.assert_not_called()


@pytest.mark.asyncio
async def test_execute_image_fanout_cancellation_releases_reservation():
    mock_context = MagicMock()
    mock_context.service._scheduler = REAL_SCHEDULER
    mock_request = _make_mock_request()
    payload = ResponsesRequest(
        model="gpt-4o",
        input=[{"type": "message", "role": "user", "content": "draw"}],
        instructions="gen",
    )
    mock_reservation = MagicMock()

    async def mock_prime_blocking(req, upstream, headers, on_error=None):
        await asyncio.sleep(10)
        return upstream, None

    mock_release = AsyncMock()
    mock_finalize = AsyncMock()

    task = asyncio.create_task(
        execute_image_fanout(
            context=mock_context,
            request=mock_request,
            responses_payload=payload,
            api_key=None,
            reservation=mock_reservation,
            rate_limit_headers={},
            public_model="gpt-image-2",
            route="generations",
            n=2,
            started_at=1000.0,
            prime_upstream_stream=mock_prime_blocking,
            logged_error_json_response=lambda *a, **k: None,
            status_for_image_error_envelope=lambda e: 500,
            release_reservation=mock_release,
            finalize_image_reservation=mock_finalize,
            resolve_client_host=lambda r: "127.0.0.1",
        )
    )
    await asyncio.sleep(0.01)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task

    mock_release.assert_awaited_once_with(mock_reservation)
    mock_finalize.assert_not_called()
