from __future__ import annotations

import pytest

from app.core.balancer.logic import (
    HEALTH_TIER_HEALTHY,
    AccountState,
    calculate_pace_deviation,
    select_account,
)
from app.db.models import AccountStatus

pytestmark = pytest.mark.unit

SECONDS_PER_DAY = 86400
SECONDS_PER_WEEK = 7 * SECONDS_PER_DAY


def test_calculate_pace_deviation_weekly() -> None:
    current = 1000000.0
    # Window ends in 3.5 days (halfway through 7-day window, expected used = 50%)
    reset_at = int(current + 3.5 * SECONDS_PER_DAY)

    # Hot account: 70% used -> +20% deviation
    hot_state = AccountState(
        account_id="acc-hot",
        status=AccountStatus.ACTIVE,
        secondary_used_percent=70.0,
        secondary_reset_at=reset_at,
    )
    dev_hot = calculate_pace_deviation(hot_state, current, secondary=True)
    assert dev_hot is not None
    assert pytest.approx(dev_hot, abs=1.0) == 20.0

    # Cool/surplus account: 30% used -> -20% deviation
    cool_state = AccountState(
        account_id="acc-cool",
        status=AccountStatus.ACTIVE,
        secondary_used_percent=30.0,
        secondary_reset_at=reset_at,
    )
    dev_cool = calculate_pace_deviation(cool_state, current, secondary=True)
    assert dev_cool is not None
    assert pytest.approx(dev_cool, abs=1.0) == -20.0


def test_calculate_pace_deviation_missing_returns_none() -> None:
    current = 1000000.0
    state = AccountState(
        account_id="acc-none",
        status=AccountStatus.ACTIVE,
        secondary_used_percent=None,
        secondary_reset_at=None,
    )
    assert calculate_pace_deviation(state, current) is None


def test_pace_aware_routing_prioritizes_surplus_account() -> None:
    current = 1000000.0
    # Both reset at the same time: 3.5 days remaining (expected: 50%)
    reset_at = int(current + 3.5 * SECONDS_PER_DAY)

    # Hot account: 65% used (ahead of pace)
    acc_hot = AccountState(
        account_id="acc-hot",
        status=AccountStatus.ACTIVE,
        health_tier=HEALTH_TIER_HEALTHY,
        secondary_used_percent=65.0,
        used_percent=20.0,
        secondary_reset_at=reset_at,
        reset_at=current + 3600,
    )

    # Cool account: 35% used (behind pace, has surplus)
    acc_cool = AccountState(
        account_id="acc-cool",
        status=AccountStatus.ACTIVE,
        health_tier=HEALTH_TIER_HEALTHY,
        secondary_used_percent=35.0,
        used_percent=20.0,
        secondary_reset_at=reset_at,
        reset_at=current + 3600,
    )

    result = select_account(
        [acc_hot, acc_cool],
        now=current,
        routing_strategy="usage_weighted",
        pace_aware=True,
    )

    assert result.account is not None
    assert result.account.account_id == "acc-cool", "Pace-aware routing must prioritize account with pace surplus"
