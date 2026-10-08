"""Record concrete egress while preserving the client's automatic fallback mode."""

from __future__ import annotations

from unittest.mock import AsyncMock, Mock

import pytest

from app.modules.proxy import service
from app.modules.proxy._service.streaming import retry
from tests.unit.test_proxy_utils import _capture_stream_retry_transport, _make_transport_policy_payload

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("configured", "resolved", "expected_mode", "expected_label"),
    [
        ("auto", "websocket", "auto", "websocket"),
        ("auto", "http", "http", "http"),
        ("http", "websocket", "http", "http"),
    ],
)
async def test_sticky_raw_attempt_records_concrete_transport_and_preserves_mode(
    monkeypatch, configured: str, resolved: str, expected_mode: str, expected_label: str
) -> None:
    write_log = AsyncMock()
    decision = Mock()
    monkeypatch.setattr(service.ProxyService, "_write_request_log", write_log)
    monkeypatch.setattr(retry, "_record_upstream_transport_decision", decision)
    mode = await _capture_stream_retry_transport(
        monkeypatch,
        upstream_config=configured,
        resolved_base_transport=resolved,
        payload=_make_transport_policy_payload(prompt_cache_key="retained-thread"),
    )

    assert mode == expected_mode
    assert write_log.await_count == 1
    assert write_log.await_args is not None
    assert write_log.await_args.kwargs["upstream_transport"] == expected_label
    assert write_log.await_args.kwargs["transport"] == "http"
    assert decision.call_count == 1
    assert decision.call_args.kwargs["upstream_transport"] == expected_label
