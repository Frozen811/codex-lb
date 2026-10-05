from __future__ import annotations

import pytest

from app.core.balancer import AccountState, select_account
from app.db.models import AccountStatus
from app.modules.proxy._load_balancer.tunables import RoutingTunables
from app.modules.proxy._load_balancer.types import RuntimeState
from app.modules.proxy.load_balancer import _state_from_account
from tests.unit.test_routing_tunables import _account, _usage

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("seed", [None, "thread-a", "thread-b"])
@pytest.mark.parametrize("zero_scores", [False, True])
def test_relative_availability_fallback_preserves_persisted_order(seed, zero_scores):
    states = [
        AccountState(
            account_id=account_id,
            status=AccountStatus.ACTIVE,
            used_percent=99,
            secondary_used_percent=99,
            persisted_used_percent=10,
            persisted_secondary_used_percent=used,
            capacity_credits=0 if zero_scores else 7560,
            plan_type="plus",
            secondary_reset_at=1_800_000_000 + 604800,
            selection_weight_multiplier=0,
        )
        for account_id, used in [("a-heavy", 95), ("z-light", 38)]
    ]
    result = select_account(states, now=1_800_000_000, routing_strategy="relative_availability", selection_seed=seed)
    assert result.account is not None and result.account.account_id == "z-light"


@pytest.mark.parametrize("tokens, weight, expected", [(10240, 0, 38), (5120, 2, 39), (16384, 1, 39.6)])
def test_lease_pressure_scales_with_estimates_and_can_be_disabled(tokens, weight, expected):
    account = _account("estimate-owner")
    state = _state_from_account(
        account=account,
        primary_entry=_usage(account.id, 38, 1_800_000_000),
        secondary_entry=None,
        runtime=RuntimeState(leased_tokens=tokens),
        now=1_800_000_000,
        routing_tunables=RoutingTunables(inflight_penalty_pct=0, lease_token_weight=weight),
        soft_drain_enabled=False,
    )
    assert state.used_percent == pytest.approx(expected)
    assert state.persisted_used_percent == 38


def test_lease_pressure_preserves_unknown_usage():
    state = _state_from_account(
        account=_account("unknown-usage-owner"),
        primary_entry=None,
        secondary_entry=None,
        runtime=RuntimeState(inflight_streams=100, leased_tokens=10240 * 100),
        now=1_800_000_000,
        soft_drain_enabled=False,
    )
    assert state.used_percent is None and state.secondary_used_percent is None
