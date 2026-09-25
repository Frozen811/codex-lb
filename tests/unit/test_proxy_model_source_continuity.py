from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest
from starlette.requests import Request

import app.modules.proxy.api as proxy_api
from app.core.openai.requests import ResponsesRequest


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_responses_model_source_with_continuity_turn_state_suppression(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_mock = Mock()
    source_selection = (source_mock, "upstream-model-v1")
    monkeypatch.setattr(proxy_api, "_select_responses_model_source", AsyncMock(return_value=source_selection))

    context = Mock()
    service = Mock()
    context.service = service
    service._resolve_websocket_previous_response_owner = AsyncMock(return_value=None)
    service._resolve_compact_turn_state_owner = AsyncMock(return_value="acc_turn_owner_1")

    # 1. Request with x-codex-turn-state resolving to an account -> suppressed
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/v1/responses",
        "headers": [(b"x-codex-turn-state", b"turn_state_123")],
    }
    request = Request(scope)
    payload = ResponsesRequest(model="gpt-5.1", instructions="", input="hello")

    sel, suppressed = await proxy_api._select_responses_model_source_with_continuity(
        request,
        payload,
        context,
        api_key=None,
    )
    assert sel is None
    assert suppressed is True
    service._resolve_compact_turn_state_owner.assert_awaited_once_with(
        turn_state="turn_state_123",
        api_key=None,
        fail_on_missing=False,
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_responses_model_source_with_continuity_turn_state_miss_routes_to_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_mock = Mock()
    source_selection = (source_mock, "upstream-model-v1")
    monkeypatch.setattr(proxy_api, "_select_responses_model_source", AsyncMock(return_value=source_selection))

    context = Mock()
    service = Mock()
    context.service = service
    service._resolve_websocket_previous_response_owner = AsyncMock(return_value=None)
    service._resolve_compact_turn_state_owner = AsyncMock(return_value=None)

    # 2. Request with turn-state not resolving to any subscription account -> routes to model source
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/v1/responses",
        "headers": [(b"turn-state", b"turn_state_unowned")],
    }
    request = Request(scope)
    payload = ResponsesRequest(model="gpt-5.1", instructions="", input="hello")

    sel, suppressed = await proxy_api._select_responses_model_source_with_continuity(
        request,
        payload,
        context,
        api_key=None,
    )
    assert sel == source_selection
    assert suppressed is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_responses_model_source_with_continuity_previous_response_suppression(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_mock = Mock()
    source_selection = (source_mock, "upstream-model-v1")
    monkeypatch.setattr(proxy_api, "_select_responses_model_source", AsyncMock(return_value=source_selection))

    context = Mock()
    service = Mock()
    context.service = service
    service._resolve_websocket_previous_response_owner = AsyncMock(return_value="acc_prev_resp_owner")
    service._resolve_compact_turn_state_owner = AsyncMock(return_value=None)

    # 3. Request with previous_response_id resolving to an account -> suppressed
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/v1/responses",
        "headers": [],
    }
    request = Request(scope)
    payload = ResponsesRequest(model="gpt-5.1", instructions="", input="hello", previous_response_id="resp_123")

    sel, suppressed = await proxy_api._select_responses_model_source_with_continuity(
        request,
        payload,
        context,
        api_key=None,
    )
    assert sel is None
    assert suppressed is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_select_responses_model_source_with_continuity_previous_response_miss_routes_to_source(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    source_mock = Mock()
    source_selection = (source_mock, "upstream-model-v1")
    monkeypatch.setattr(proxy_api, "_select_responses_model_source", AsyncMock(return_value=source_selection))

    context = Mock()
    service = Mock()
    context.service = service
    service._resolve_websocket_previous_response_owner = AsyncMock(return_value=None)
    service._resolve_compact_turn_state_owner = AsyncMock(return_value=None)

    # 4. Request with previous_response_id not resolving -> routes to model source
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/v1/responses",
        "headers": [],
    }
    request = Request(scope)
    payload = ResponsesRequest(model="gpt-5.1", instructions="", input="hello", previous_response_id="resp_unowned")

    sel, suppressed = await proxy_api._select_responses_model_source_with_continuity(
        request,
        payload,
        context,
        api_key=None,
    )
    assert sel == source_selection
    assert suppressed is False
