from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy.orm.attributes import set_attribute

from app.core.usage import clear_plan_capacity_overrides, set_plan_capacity_override
from app.core.usage.pricing import UsageTokens, calculate_cost_from_usage, get_pricing_for_model
from app.core.utils.time import naive_utc_to_epoch
from app.db.models import UsageHistory
from app.modules.accounts.schemas import AccountSummary
from app.modules.dashboard.weekly_cost import weekly_cost_windows


@pytest.mark.parametrize("capacity", [float("nan"), float("inf"), float("-inf"), True])
def test_capacity_override_rejects_nonfinite_and_boolean_values(capacity):
    try:
        with pytest.raises(ValueError):
            set_plan_capacity_override("pro", "secondary", capacity)
    finally:
        clear_plan_capacity_overrides()


@pytest.mark.parametrize("model", ["gpt-5.6-luna", "gpt-5.6-luna-2026-07-30"])
def test_luna_current_prices_distinguish_cached_input_and_output(model):
    resolved = get_pricing_for_model(model)
    assert resolved is not None
    cost = calculate_cost_from_usage(
        UsageTokens(input_tokens=200_000, cached_input_tokens=100_000, output_tokens=1_000_000), resolved[1]
    )
    assert cost == pytest.approx(1.222)


def test_luna_long_context_uses_explicit_higher_rates():
    resolved = get_pricing_for_model("gpt-5.6-luna")
    assert resolved is not None
    cost = calculate_cost_from_usage(
        UsageTokens(input_tokens=1_000_000, cached_input_tokens=500_000, output_tokens=1_000_000), resolved[1]
    )
    assert cost == pytest.approx(2.02)


@pytest.mark.parametrize(
    "invalid",
    [
        "one_sample",
        "zero_delta",
        "decreasing",
        "reset",
        "missing_reset",
        "stale",
        "monthly",
        "paused",
        "unknown_percent",
        "duplicate_time",
        "negative_percent",
        "nonfinite_percent",
        "future",
        "expired",
    ],
)
def test_weekly_cost_intervals_reject_unmatched_observations(invalid):
    now = datetime(2026, 10, 14, 12)
    reset = now + timedelta(days=2)
    summary = AccountSummary(
        account_id="a",
        email="a@example.invalid",
        display_name="a",
        plan_type="pro",
        status="active",
        reset_at_secondary=reset,
        window_minutes_secondary=10080,
    )
    rows = [
        UsageHistory(
            account_id="a",
            used_percent=used,
            window="secondary",
            window_minutes=10080,
            reset_at=int(naive_utc_to_epoch(reset)),
            recorded_at=at,
        )
        for at, used in [(now - timedelta(hours=2), 10), (now, 20)]
    ]
    if invalid == "one_sample":
        rows = rows[-1:]
    elif invalid == "zero_delta":
        rows[-1].used_percent = 10
    elif invalid == "decreasing":
        rows[-1].used_percent = 5
    elif invalid == "reset":
        assert rows[0].reset_at is not None
        rows[0].reset_at -= 3600
    elif invalid == "missing_reset":
        rows[-1].reset_at = None
    elif invalid == "stale":
        rows[-1].recorded_at -= timedelta(minutes=10)
    elif invalid == "monthly":
        summary.window_minutes_secondary = 43200
    elif invalid == "paused":
        summary.status = "paused"
    elif invalid == "unknown_percent":
        set_attribute(rows[-1], "used_percent", None)
    elif invalid == "duplicate_time":
        rows[-1].recorded_at = rows[0].recorded_at
    elif invalid == "negative_percent":
        rows[-1].used_percent = -1
    elif invalid == "nonfinite_percent":
        rows[-1].used_percent = float("nan")
    elif invalid == "future":
        rows[-1].recorded_at = now + timedelta(hours=1)
    elif invalid == "expired":
        summary.reset_at_secondary = now - timedelta(seconds=1)
    assert weekly_cost_windows([summary], {"a": rows}, now, 300) == []
