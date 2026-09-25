from __future__ import annotations

import math

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from app.core.balancer.logic import (
    HEALTH_TIER_DRAINING,
    HEALTH_TIER_HEALTHY,
    HEALTH_TIER_PROBING,
    ROUTING_POLICY_BURN_FIRST,
    ROUTING_POLICY_NORMAL,
    ROUTING_POLICY_PRESERVE,
    AccountState,
    select_account,
)
from app.db.models import AccountStatus
from app.modules.proxy._load_balancer.sticky_selection import _select_account_preferring_budget_safe

pytestmark = pytest.mark.unit

account_statuses = st.sampled_from(
    [
        AccountStatus.ACTIVE,
        AccountStatus.DEACTIVATED,
        AccountStatus.PAUSED,
        AccountStatus.RATE_LIMITED,
        AccountStatus.REAUTH_REQUIRED,
        AccountStatus.QUOTA_EXCEEDED,
    ]
)

health_tiers = st.sampled_from(
    [
        HEALTH_TIER_HEALTHY,
        HEALTH_TIER_PROBING,
        HEALTH_TIER_DRAINING,
        -1,
        99,
    ]
)

routing_policies = st.sampled_from(
    [
        ROUTING_POLICY_NORMAL,
        ROUTING_POLICY_BURN_FIRST,
        ROUTING_POLICY_PRESERVE,
    ]
)

routing_strategies = st.sampled_from(
    [
        "capacity_weighted",
        "round_robin",
        "usage_weighted",
        "sequential_drain",
        "reset_drain",
        "relative_availability",
        "fill_first",
    ]
)

floats_or_none = st.one_of(
    st.none(),
    st.floats(min_value=-500.0, max_value=500.0, allow_nan=False),
)

account_state_strategy = st.builds(
    AccountState,
    account_id=st.text(min_size=1, max_size=15, alphabet="abcdefghijklmnopqrstuvwxyz0123456789-"),
    status=account_statuses,
    health_tier=health_tiers,
    used_percent=floats_or_none,
    secondary_used_percent=floats_or_none,
    reset_at=floats_or_none,
    secondary_reset_at=st.one_of(st.none(), st.integers(min_value=0, max_value=2_000_000_000)),
    routing_policy=routing_policies,
    error_count=st.integers(min_value=0, max_value=100),
    selection_weight_multiplier=st.floats(min_value=0.0, max_value=10.0, allow_nan=False),
)


@given(
    states=st.lists(account_state_strategy, min_size=1, max_size=10, unique_by=lambda s: s.account_id),
    strategy=routing_strategies,
    now=st.floats(min_value=1_000_000.0, max_value=2_000_000.0, allow_nan=False),
)
@settings(max_examples=100, deadline=None)
def test_fuzz_select_account_never_crashes(
    states: list[AccountState],
    strategy: str,
    now: float,
) -> None:
    # Invoking select_account must handle any arbitrary permutation of states safely
    result = select_account(
        states,
        now=now,
        routing_strategy=strategy,
        allow_backoff_fallback=True,
    )
    if result.account is not None:
        assert isinstance(result.account.account_id, str)


@given(
    states=st.lists(account_state_strategy, min_size=2, max_size=10, unique_by=lambda s: s.account_id),
    now=st.floats(min_value=1_000_000.0, max_value=2_000_000.0, allow_nan=False),
)
@settings(max_examples=100, deadline=None)
def test_fuzz_select_account_inactive_invariant(
    states: list[AccountState],
    now: float,
) -> None:
    # Ensure any non-active account is not selected unless specific probe conditions apply
    # Set all accounts to PAUSED or DEACTIVATED
    inactive_states = [
        AccountState(
            account_id=s.account_id,
            status=AccountStatus.DEACTIVATED,
            health_tier=s.health_tier,
            used_percent=s.used_percent,
        )
        for s in states
    ]
    result = select_account(
        inactive_states,
        now=now,
        routing_strategy="round_robin",
        allow_backoff_fallback=False,
    )
    assert result.account is None, "Deactivated accounts must never be selected for normal routing"


@given(
    states=st.lists(account_state_strategy, min_size=1, max_size=8, unique_by=lambda s: s.account_id),
    strategy=routing_strategies,
    threshold=st.floats(min_value=10.0, max_value=95.0, allow_nan=False),
)
@settings(max_examples=75, deadline=None)
def test_fuzz_budget_safe_selection_invariants(
    states: list[AccountState],
    strategy: str,
    threshold: float,
) -> None:
    active_states = []
    for s in states:
        ht = s.health_tier if s.health_tier in (HEALTH_TIER_HEALTHY, HEALTH_TIER_DRAINING) else HEALTH_TIER_HEALTHY
        used = s.used_percent if s.used_percent is not None and not math.isnan(s.used_percent) else 50.0
        sec_used = (
            s.secondary_used_percent
            if s.secondary_used_percent is not None and not math.isnan(s.secondary_used_percent)
            else 50.0
        )
        active_states.append(
            AccountState(
                account_id=s.account_id,
                status=AccountStatus.ACTIVE,
                health_tier=ht,
                used_percent=used,
                secondary_used_percent=sec_used,
            )
        )
    result = _select_account_preferring_budget_safe(
        active_states,
        prefer_earlier_reset=False,
        routing_strategy=strategy,
        budget_threshold_pct=threshold,
    )
    if result.account is not None:
        assert any(s.account_id == result.account.account_id for s in active_states)
