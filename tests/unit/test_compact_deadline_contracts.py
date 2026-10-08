"""Compact total budgets and SSE idle deadlines remain independently bounded."""

from __future__ import annotations

from typing import cast
from unittest.mock import AsyncMock

import pytest

from app.core.clients import proxy
from app.core.config.settings import Settings
from app.core.openai.requests import ResponsesCompactRequest
from app.modules.automations.repository import run_claim_timeout_seconds
from tests.unit.test_proxy_utils import _compact_sse_response, _CompactSession

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("configured", "remaining", "expected_total", "expected_idle"),
    [(900.0, None, 900.0, 45.0), (60.0, None, 60.0, 45.0), (900.0, 30.0, 30.0, 30.0), (60.0, 120.0, 60.0, 120.0)],
)
async def test_compact_collection_keeps_total_and_idle_deadlines(
    monkeypatch, configured: float, remaining: float | None, expected_total: float, expected_idle: float
) -> None:
    settings = Settings(_env_file=None, compact_request_budget_seconds=configured, stream_idle_timeout_seconds=45.0)
    monkeypatch.setattr(proxy, "get_settings", lambda: settings)
    collector = AsyncMock(wraps=proxy._compact_response_payload_from_success_response)
    monkeypatch.setattr(proxy, "_compact_response_payload_from_success_response", collector)
    session = _CompactSession(_compact_sse_response(response_id="resp_deadline", encrypted_content="enc_deadline"))
    payload = ResponsesCompactRequest.model_validate({"model": "gpt-5.1", "instructions": "compact", "input": []})
    tokens = proxy.push_compact_timeout_overrides(total_timeout_seconds=remaining)
    try:
        result = await proxy.compact_responses(
            payload,
            headers={},
            access_token="token",
            account_id="acc_deadline",
            session=cast(proxy.aiohttp.ClientSession, session),
        )
    finally:
        proxy.pop_compact_timeout_overrides(tokens)

    timeout = session.calls[0]["timeout"]
    assert isinstance(timeout, proxy.aiohttp.ClientTimeout)
    assert timeout.total == pytest.approx(expected_total, abs=0.1)
    assert collector.await_args is not None
    assert collector.await_args.kwargs["idle_timeout_seconds"] == expected_idle
    assert result.model_dump(mode="json")["output"][0]["encrypted_content"] == "enc_deadline"


def test_default_compact_budget_bounds_automation_claim_reclaim() -> None:
    settings = Settings(_env_file=None)
    assert settings.compact_request_budget_seconds == 900.0
    assert run_claim_timeout_seconds(None, fallback_budget_seconds=settings.compact_request_budget_seconds) == 930.0
    assert run_claim_timeout_seconds(60.0, fallback_budget_seconds=settings.compact_request_budget_seconds) == 930.0
    assert run_claim_timeout_seconds(1200.0, fallback_budget_seconds=settings.compact_request_budget_seconds) == 1230.0
