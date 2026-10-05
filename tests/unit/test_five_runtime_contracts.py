from __future__ import annotations

import pytest

from app.core.balancer.logic import failover_outcome
from app.core.balancer.types import UpstreamError
from app.core.clients import proxy, proxy_websocket
from app.core.usage.pricing import UsageTokens, calculate_cost_from_usage, get_pricing_for_model
from app.modules.proxy.helpers import classify_upstream_failure

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("identity", ["ccodex-internal", "ccodex-handoff-worker"])
@pytest.mark.parametrize("signal", ["originator", "user-agent", "both"])
@pytest.mark.parametrize(
    "builder",
    [
        proxy._build_upstream_headers,
        proxy._build_upstream_websocket_headers,
        proxy_websocket._build_upstream_websocket_headers,
    ],
)
def test_ccodex_native_fingerprint_survives_all_builders(identity, signal, builder):
    inbound = {"Version": "0.159.3"}
    if signal in ("user-agent", "both"):
        inbound["User-Agent"] = f"{identity}/0.159.3 (Ubuntu 24.4.0; x86_64) unknown"
    if signal in ("originator", "both"):
        inbound["originator"] = identity
    headers = {k.lower(): v for k, v in builder(inbound, "fixture-access", "fixture-account").items()}
    assert headers["version"] == "0.159.3"
    for key, value in inbound.items():
        assert headers[key.lower()] == value
    assert proxy._is_native_codex_request(inbound)


@pytest.mark.parametrize("identity", ["ccodex-internal-evil", "ccodex-handoff-worker-other", "ccodex-unknown"])
def test_gateway_lookalikes_remain_non_native(identity):
    inbound = {"User-Agent": f"{identity}/0.159.3", "originator": identity, "x-codex-turn-state": "state"}
    assert not proxy._is_native_codex_request(inbound)
    headers = proxy._build_upstream_headers(inbound, "fixture-access", "fixture-account")
    assert headers["User-Agent"].startswith("codex_cli_rs/")


@pytest.mark.parametrize("status", [402, None, 500])
def test_workspace_deactivation_is_exact_and_excludes_selection(status):
    failure = classify_upstream_failure(
        error_code="deactivated_workspace",
        error=UpstreamError(message="unavailable"),
        http_status=status,
        phase="first_event",
    )
    assert failure["failure_class"] == "account_unavailable"
    assert failure["excludes_account"]


@pytest.mark.parametrize(
    "visible,owned,more,action,ended",
    [
        (False, False, True, "failover_next", None),
        (True, False, True, "surface", None),
        (False, True, True, "surface", None),
        (False, False, False, "surface", "pool_exhausted"),
    ],
)
def test_workspace_failover_retains_walk_endings_and_ownership(visible, owned, more, action, ended):
    result = failover_outcome(
        failure_class="account_unavailable",
        downstream_visible=visible,
        owner_bound=owned,
        same_account_retry_available=True,
        more_candidates_possible=more,
    )
    assert (result.action, result.ended_by) == (action, ended)


@pytest.mark.parametrize("model", ["gpt-6-astra", "gpt-6-astra-2026-09-01"])
@pytest.mark.parametrize(
    "input_tokens,cached_tokens,expected",
    [
        (100000, 0, 9.0),
        (272000, 20000, 18.24),
        (272001, 20000, 34.98012),
    ],
)
def test_bundled_ultrafast_rates(model, input_tokens, cached_tokens, expected):
    resolved = get_pricing_for_model(model)
    assert resolved is not None
    assert calculate_cost_from_usage(
        UsageTokens(input_tokens, 10000, cached_tokens), resolved[1], service_tier=" UltraFast "
    ) == pytest.approx(expected)
