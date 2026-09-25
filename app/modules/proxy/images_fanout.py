from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any, Callable

from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.core.clients.proxy import ProxyResponseError
from app.core.clock import clock_for
from app.core.openai.images import V1ImageResponse, V1ImageUsage
from app.core.types import JsonValue
from app.modules.proxy import images_service as images_service_module
from app.modules.proxy.images_observability import (
    ImageRoute,
    record_images_route_observability,
)

if TYPE_CHECKING:
    from app.core.openai.requests import ResponsesRequest
    from app.dependencies import ProxyContext
    from app.modules.api_keys.service import ApiKeyData, ApiKeyUsageReservationData


async def execute_image_fanout(
    *,
    context: ProxyContext,
    request: Request,
    responses_payload: ResponsesRequest,
    api_key: ApiKeyData | None,
    reservation: ApiKeyUsageReservationData | None,
    rate_limit_headers: dict[str, str],
    public_model: str,
    route: ImageRoute,
    n: int,
    started_at: float,
    prime_upstream_stream: Callable[..., Any],
    logged_error_json_response: Callable[..., Any],
    status_for_image_error_envelope: Callable[..., Any],
    release_reservation: Callable[..., Any],
    finalize_image_reservation: Callable[..., Any],
    resolve_client_host: Callable[..., Any],
) -> Response:
    """Execute ``n`` image generation calls concurrently and aggregate the results."""

    async def _run_single_call(
        idx: int,
    ) -> tuple[V1ImageResponse | None, Response | None, dict[str, object]]:
        captured: dict[str, object] = {}
        upstream = context.service.stream_responses(
            responses_payload,
            request.headers,
            codex_session_affinity=False,
            propagate_http_errors=True,
            openai_cache_affinity=True,
            api_key=api_key,
            api_key_reservation=None,
            client_ip=resolve_client_host(request),
        )
        try:
            primed_upstream, prime_error = await prime_upstream_stream(
                request,
                upstream,
                rate_limit_headers,
                on_error=None,
            )
            if prime_error is not None:
                return None, prime_error, captured

            assert primed_upstream is not None
            response_payload, error_envelope = await images_service_module.collect_responses_stream_for_images(
                primed_upstream,
                captured=captured,
            )
            if error_envelope is not None:
                error_status = status_for_image_error_envelope(error_envelope)
                err_resp = logged_error_json_response(
                    request,
                    error_status,
                    error_envelope,
                    headers=rate_limit_headers,
                )
                return None, err_resp, captured

            assert response_payload is not None
            images_result = images_service_module.images_response_from_responses(response_payload)
            if not isinstance(images_result, V1ImageResponse):
                img_status = status_for_image_error_envelope(images_result)
                err_resp = logged_error_json_response(
                    request,
                    img_status,
                    images_result,
                    headers=rate_limit_headers,
                )
                return None, err_resp, captured

            return images_result, None, captured
        except ProxyResponseError as exc:
            err_resp = logged_error_json_response(
                request,
                exc.status_code,
                exc.payload,
                headers=rate_limit_headers,
            )
            return None, err_resp, captured

    tasks = [_run_single_call(i) for i in range(n)]
    results = await asyncio.gather(*tasks)

    for img_result, err_resp, captured in results:
        if err_resp is not None:
            await release_reservation(reservation)
            status = getattr(err_resp, "status_code", 500)
            record_images_route_observability(
                route=route,
                model=public_model,
                stream=False,
                status=status,
                outcome="upstream_error",
                started_at=started_at,
                fanout=n,
            )
            return err_resp

    all_data = []
    total_input = 0
    total_output = 0
    total_cached = 0
    has_tokens = False

    for img_result, _, captured in results:
        assert img_result is not None
        all_data.extend(img_result.data)

        _input = captured.get("image_input_tokens")
        _output = captured.get("image_output_tokens")
        _cached = captured.get("image_cached_input_tokens")
        if isinstance(_input, int):
            total_input += _input
            has_tokens = True
        if isinstance(_output, int):
            total_output += _output
            has_tokens = True
        if isinstance(_cached, int):
            total_cached += _cached

        response_id = captured.get("response_id")
        if response_id and isinstance(response_id, str):
            await context.service.rewrite_request_log_model(response_id, public_model)

    await finalize_image_reservation(
        context.service,
        api_key,
        reservation,
        model=public_model,
        input_tokens=total_input if has_tokens else None,
        output_tokens=total_output if has_tokens else None,
        cached_input_tokens=total_cached if total_cached > 0 else None,
    )

    usage = None
    if has_tokens:
        input_details: dict[str, JsonValue] | None = {"cached_tokens": total_cached} if total_cached > 0 else None
        usage = V1ImageUsage(
            input_tokens=total_input,
            output_tokens=total_output,
            total_tokens=total_input + total_output,
            input_tokens_details=input_details,
        )

    record_images_route_observability(
        route=route,
        model=public_model,
        stream=False,
        status=200,
        outcome="success",
        started_at=started_at,
        fanout=n,
    )
    combined = V1ImageResponse(
        created=int(clock_for(context.service).time()),
        data=all_data,
        usage=usage,
    )
    return JSONResponse(
        content=combined.model_dump(mode="json", exclude_none=True),
        headers=rate_limit_headers,
    )
