from __future__ import annotations

from datetime import datetime, timedelta
from time import perf_counter
from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy import Table, insert

from app.db.models import RequestLog
from app.db.session import SessionLocal
from app.modules.reports.cache import ReportsCaches
from app.modules.reports.repository import ReportsRepository
from app.modules.reports.rollup import fold_next_report_slice

pytestmark = pytest.mark.integration
BASE = datetime(2026, 9, 14)
ROW_COUNT = 543_000


async def test_dense_seven_day_reports_api_raw_folded_and_cached(async_client, app_instance, db_setup, monkeypatch):
    async with SessionLocal() as session:
        for offset in range(0, ROW_COUNT, 5000):
            await session.execute(
                insert(cast(Table, RequestLog.__table__)),
                [
                    {
                        "request_id": f"dense-report-{i}",
                        "requested_at": BASE + timedelta(days=i % 7, seconds=i // 7),
                        "model": "dense-model",
                        "status": "success",
                        "request_kind": "normal",
                        "useragent_group": "CLI",
                        "conversation_id": f"thread-{i % 10}",
                        "input_tokens": 100,
                        "output_tokens": 50,
                        "reasoning_tokens": 30,
                        "cached_input_tokens": 20,
                        "cost_usd": 0.01,
                        "latency_first_token_ms": 125,
                        "latency_first_output_ms": 500,
                        "latency_upstream_terminal_ms": 1000,
                        "latency_ms": 3000,
                        "latency_queue_ms": 10,
                        "output_delta_count": 4,
                    }
                    for i in range(offset, min(offset + 5000, ROW_COUNT))
                ],
            )
        await session.commit()

    query = {"start_date": "2026-09-14", "end_date": "2026-09-20", "timezone": "UTC"}
    started = perf_counter()
    raw = await async_client.get("/api/reports", params=query)
    raw_seconds = perf_counter() - started
    assert raw.status_code == 200
    expected = raw.json()
    assert expected["summary"]["totalRequests"] == ROW_COUNT
    assert expected["summary"]["totalConversations"] == 10
    assert expected["summary"]["totalInputTokens"] == ROW_COUNT * 100
    assert expected["summary"]["totalOutputTokens"] == ROW_COUNT * 50
    assert expected["summary"]["totalCostUsd"] == pytest.approx(ROW_COUNT * 0.01)
    assert expected["speedMetricsAvailable"] is True
    assert sum(row["tpsSampleCount"] for row in expected["daily"]) == ROW_COUNT
    assert all(
        row["medianTtftMs"] == 125 and row["medianTps"] == 40 and row["medianQueueMs"] == 10
        for row in expected["daily"]
    )

    async with SessionLocal() as session:
        while await fold_next_report_slice(session, BASE + timedelta(days=7)):
            pass
    app_instance.state.reports_caches = ReportsCaches()
    started = perf_counter()
    folded = await async_client.get("/api/reports", params=query)
    folded_seconds = perf_counter() - started
    assert folded.status_code == 200
    actual = folded.json()
    expected.pop("generatedAt")
    actual.pop("generatedAt")
    assert actual == expected

    monkeypatch.setattr(ReportsRepository, "aggregate_summary", AsyncMock(side_effect=AssertionError("cache miss")))
    started = perf_counter()
    cached = await async_client.get("/api/reports", params=query)
    cached_seconds = perf_counter() - started
    assert cached.status_code == 200
    assert cached.json() == folded.json()
    print(
        f"dense report rows={ROW_COUNT} raw={raw_seconds:.3f}s "
        f"folded={folded_seconds:.3f}s cached={cached_seconds:.3f}s"
    )
