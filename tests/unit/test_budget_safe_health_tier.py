from __future__ import annotations

import pytest

from app.core.balancer.logic import (
    HEALTH_TIER_HEALTHY,
    AccountState,
)
from app.db.models import AccountStatus
from app.modules.proxy._load_balancer.sticky_selection import _select_account_preferring_budget_safe

pytestmark = pytest.mark.unit


def _make_state(
    account_id: str,
    health_tier: int,
    used_percent: float,
    status: AccountStatus = AccountStatus.ACTIVE,
) -> AccountState:
    return AccountState(
        account_id=account_id,
        status=status,
        health_tier=health_tier,
        used_percent=used_percent,
        secondary_used_percent=used_percent,
    )


def test_healthy_above_budget_preferred_over_draining_below_budget() -> None:
    from app.core.balancer.logic import HEALTH_TIER_DRAINING

    # Account A: Healthy, but 85% used (above 80% threshold)
    acc_a = _make_state("acc-a", health_tier=HEALTH_TIER_HEALTHY, used_percent=85.0)
    # Account B: Draining, only 10% used (below 80% threshold)
    acc_b = _make_state("acc-b", health_tier=HEALTH_TIER_DRAINING, used_percent=10.0)

    result = _select_account_preferring_budget_safe(
        [acc_a, acc_b],
        prefer_earlier_reset=False,
        routing_strategy="round_robin",
        budget_threshold_pct=80.0,
    )

    assert result.account is not None
    assert result.account.account_id == "acc-a", "Healthy tier must dominate lower health tier despite usage threshold"


def test_budget_safe_applies_within_same_health_tier() -> None:
    # Account A: Healthy, 70% used (budget-safe)
    acc_a = _make_state("acc-a", health_tier=HEALTH_TIER_HEALTHY, used_percent=70.0)
    # Account B: Healthy, 90% used (above threshold)
    acc_b = _make_state("acc-b", health_tier=HEALTH_TIER_HEALTHY, used_percent=90.0)

    result = _select_account_preferring_budget_safe(
        [acc_a, acc_b],
        prefer_earlier_reset=False,
        routing_strategy="round_robin",
        budget_threshold_pct=80.0,
    )

    assert result.account is not None
    assert result.account.account_id == "acc-a", "Within healthy tier, budget-safe account must be chosen"
