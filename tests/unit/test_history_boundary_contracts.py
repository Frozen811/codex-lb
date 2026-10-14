from __future__ import annotations

import pytest

from app.core.openai.requests import ResponsesRequest
from app.db.models import StickySessionKind
from app.modules.proxy._load_balancer.tunables import RoutingTunables
from app.modules.proxy._service.http_bridge.helpers import _http_bridge_payload_looks_like_full_resend
from app.modules.proxy._service.support import _responses_input_items_are_self_contained
from app.modules.proxy.load_balancer import LoadBalancer
from tests.unit.test_select_with_stickiness import _active, _invoke_stickiness, _make_sticky_repo

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("call_type", ["function_call", "custom_tool_call", "apply_patch_call", "computer_call"])
@pytest.mark.parametrize("call_count,output_count,expected", [(1, 2, False), (2, 2, True), (1, 1, True)])
def test_full_resend_pairs_tool_occurrences(call_type, call_count, output_count, expected):
    call = {"type": call_type, "call_id": "reused", "name": "read", "arguments": "{}"}
    output = {"type": f"{call_type}_output", "call_id": "reused", "output": "result"}
    items = []
    for index in range(max(call_count, output_count)):
        if index < call_count:
            items.append(call.copy())
        if index < output_count:
            items.append(output.copy())
    assert _responses_input_items_are_self_contained(items) is expected
    payload = ResponsesRequest.model_validate({"model": "gpt-5.1", "instructions": "", "input": items})
    forwarded = ResponsesRequest.model_validate(payload.model_dump_for_forwarding())
    assert _http_bridge_payload_looks_like_full_resend(payload) is expected
    assert _http_bridge_payload_looks_like_full_resend(forwarded) is expected


@pytest.mark.parametrize("length", [4080, 4095, 4096, 4097, 8192])
def test_single_turn_is_stable_through_forwarding(length):
    payload = ResponsesRequest.model_validate({"model": "gpt-5.1", "instructions": "", "input": "x" * length})
    for request in [payload, ResponsesRequest.model_validate(payload.model_dump_for_forwarding())]:
        assert not _http_bridge_payload_looks_like_full_resend(request)


@pytest.mark.parametrize("call_type", ["function_call", "custom_tool_call", "apply_patch_call", "computer_call"])
def test_other_protocol_cannot_supply_a_function_output(call_type):
    items = [
        {"type": call_type, "call_id": "same"},
        {"type": "function_call_output", "call_id": "same", "output": "result"},
    ]
    assert _responses_input_items_are_self_contained(items) is (call_type == "function_call")


@pytest.mark.asyncio
@pytest.mark.parametrize("reallocate", [False, True])
async def test_sticky_thread_pressure_waits_for_boundary(reallocate, monkeypatch):
    monkeypatch.setattr(
        LoadBalancer, "current_routing_tunables", lambda self: RoutingTunables(defer_sticky_budget_reallocation=True)
    )
    repo = _make_sticky_repo("owner")
    result = await _invoke_stickiness(
        [_active("owner", used_percent=96), _active("peer", used_percent=10)],
        "thread",
        repo,
        sticky_kind=StickySessionKind.STICKY_THREAD,
        reallocate_sticky=reallocate,
        sticky_max_age_seconds=None,
    )
    assert result.account.account_id == ("peer" if reallocate else "owner")
    if reallocate:
        repo.upsert.assert_awaited_once()
    else:
        repo.upsert.assert_not_awaited()
        repo.delete.assert_not_awaited()
