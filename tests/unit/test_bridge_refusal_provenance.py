from __future__ import annotations

from contextlib import nullcontext
from typing import Any, cast
from unittest.mock import AsyncMock

import pytest

from app.core.clients.proxy import ProxyResponseError
from app.modules.proxy import service as proxy_service
from tests.unit.test_proxy_http_bridge import _make_bridge_session, _make_cooldown_suppression_request_state


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("marker", "value", "local"),
    [
        (None, None, True),
        ("response_create_attempt_count", 1, False),
        ("response_id", "resp_old", False),
        ("response_event_count", 1, False),
        ("replay_count", 1, False),
    ],
)
async def test_local_refusal_proof_excludes_previously_dispatched_states(monkeypatch, marker, value, local):
    service = proxy_service.ProxyService(cast(Any, nullcontext()))
    session = _make_bridge_session()
    state = _make_cooldown_suppression_request_state("provenance-contract")
    if marker is not None:
        setattr(state, marker, value)
    monkeypatch.setattr(service, "_http_bridge_precreated_retry_allowed", AsyncMock(return_value=False))
    monkeypatch.setattr(service, "_http_bridge_precreated_retry_block", AsyncMock(return_value=(3.0, "cooldown")))
    monkeypatch.setattr(service, "_retire_idle_http_bridge_session_on_cooldown_suppression", AsyncMock())
    with pytest.raises(ProxyResponseError) as failure:
        await service._submit_http_bridge_request(
            session, request_state=state, text_data=state.request_text or "", queue_limit=8
        )
    assert failure.value.local_pre_dispatch_refusal is local
    assert failure.value.status_code == 503
    assert failure.value.payload["error"]["code"] == "upstream_request_timeout"
    assert failure.value.retry_after_seconds == 3
    assert session.admission_waiter_count == 0
    assert not session.pending_requests
