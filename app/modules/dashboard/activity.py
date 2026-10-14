from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timedelta

from pydantic import Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils.time import to_utc_naive
from app.db.dialect_sql import epoch_seconds
from app.db.models import RequestLog, RequestUsageHourlyRollup
from app.modules.accounts.usage_time_rollup import WARMUP_REQUEST_KINDS
from app.modules.accounts.usage_time_rollup_read import epoch_to_datetime, raw_windows_clause, read_hourly_window
from app.modules.shared.schemas import DashboardModel


class RequestActivityDay(DashboardModel):
    date: date
    requests: int


class RequestActivityResponse(DashboardModel):
    start_date: date
    end_date: date
    days: list[RequestActivityDay] = Field(default_factory=list)


async def request_activity(session: AsyncSession, now: datetime) -> RequestActivityResponse:
    today = to_utc_naive(now).date()
    first_month = today.year * 12 + today.month - 1 - 5
    start = datetime(first_month // 12, first_month % 12 + 1, 1)
    until = datetime.combine(today + timedelta(days=1), datetime.min.time())
    folded, raw_windows = await read_hourly_window(
        session, start, until, filters=[RequestUsageHourlyRollup.request_kind.not_in(WARMUP_REQUEST_KINDS)]
    )
    counts: defaultdict[date, int] = defaultdict(int)
    for row in folded:
        counts[epoch_to_datetime(row.bucket_epoch).date()] += row.request_count
    if raw_windows:
        day_epoch = func.floor(epoch_seconds(RequestLog.requested_at) / 86400) * 86400
        rows = await session.execute(
            select(day_epoch.label("day_epoch"), func.count().label("requests"))
            .where(raw_windows_clause(raw_windows), RequestLog.request_kind.not_in(WARMUP_REQUEST_KINDS))
            .group_by(day_epoch)
        )
        for row in rows:
            counts[epoch_to_datetime(int(row.day_epoch)).date()] += int(row.requests)
    return RequestActivityResponse(
        start_date=start.date(),
        end_date=today,
        days=[RequestActivityDay(date=day, requests=count) for day, count in sorted(counts.items()) if count > 0],
    )
