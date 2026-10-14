from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from math import isfinite

from app.core.utils.time import naive_utc_to_epoch
from app.db.models import UsageHistory
from app.modules.accounts.schemas import AccountSummary


@dataclass(frozen=True, slots=True)
class WeeklyCostWindow:
    account_id: str
    since: datetime
    until: datetime
    used_percent: float


def weekly_cost_windows(
    summaries: list[AccountSummary],
    histories: dict[str, list[UsageHistory]],
    now: datetime,
    freshness_seconds: float,
) -> list[WeeklyCostWindow]:
    windows: list[WeeklyCostWindow] = []
    now_epoch = naive_utc_to_epoch(now)
    for summary in summaries:
        if summary.status not in {"active", "rate_limited", "quota_exceeded"}:
            continue
        if summary.window_minutes_secondary != 10080 or summary.reset_at_secondary is None:
            continue
        reset = int(naive_utc_to_epoch(summary.reset_at_secondary))
        if reset <= now_epoch:
            continue
        start_epoch = reset - timedelta(days=7).total_seconds()
        rows = sorted(histories.get(summary.account_id, []), key=lambda row: naive_utc_to_epoch(row.recorded_at))
        # A changed/reset counter ends the observation interval. Never stitch
        # quota deltas across a rollover or an in-window redemption.
        segment: list[UsageHistory] = []
        for row in rows:
            recorded_at_epoch = naive_utc_to_epoch(row.recorded_at)
            if recorded_at_epoch > now_epoch:
                continue
            if (
                row.reset_at != reset
                or row.window_minutes != 10080
                or recorded_at_epoch < start_epoch
                or row.used_percent is None
                or not isfinite(row.used_percent)
                or not 0 <= row.used_percent <= 100
            ):
                segment = []
                continue
            if segment and row.used_percent < segment[-1].used_percent:
                segment = []
            if segment and row.recorded_at == segment[-1].recorded_at:
                segment = []
            segment.append(row)
        if len(segment) < 2:
            continue
        first, latest = segment[0], segment[-1]
        if naive_utc_to_epoch(latest.recorded_at) < now_epoch - freshness_seconds:
            continue
        delta = latest.used_percent - first.used_percent
        if delta <= 0:
            continue
        windows.append(WeeklyCostWindow(summary.account_id, first.recorded_at, latest.recorded_at, delta))
    return sorted(windows, key=lambda window: window.account_id)
