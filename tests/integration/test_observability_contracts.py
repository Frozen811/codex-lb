from __future__ import annotations

from datetime import UTC, datetime, timedelta
from time import perf_counter

import pytest
from sqlalchemy import delete, event, insert

import app.core.auth.dependencies as auth_dependencies
import app.modules.dashboard.api as dashboard_api
import app.modules.request_logs.repository as logs_module
from app.core.auth.dashboard_access import DashboardPrincipal, DashboardRole
from app.core.auth.dashboard_mode import DashboardAuthMode
from app.core.auth.dependencies import validate_dashboard_session
from app.db.models import ModelSource, RequestLog
from app.db.session import SessionLocal, engine
from app.modules.accounts.usage_time_rollup import run_hourly_fold_pass
from app.modules.reports.cache import ReportsCaches
from app.modules.reports.rollup import fold_next_report_slice

pytestmark = pytest.mark.integration
NOW = datetime(2026, 10, 14, 14, tzinfo=UTC)


async def test_report_at_30000_rows_retains_folded_totals_after_raw_pruning(
    async_client, app_instance, db_setup, record_property
):
    base = datetime(2026, 6, 1)
    async with SessionLocal() as session:
        await session.execute(
            insert(RequestLog),
            [
                {
                    "request_id": f"report-scale-{i}",
                    "model": "test",
                    "status": "success",
                    "request_kind": "warmup" if i % 100 == 0 else "normal",
                    "input_tokens": 10,
                    "output_tokens": 5,
                    "requested_at": base + timedelta(seconds=i * 10),
                }
                for i in range(30000)
            ],
        )
        await session.commit()
    params = {"start_date": "2026-06-01", "end_date": "2026-06-30", "timezone": "UTC"}
    started = perf_counter()
    raw = await async_client.get("/api/reports", params=params)
    record_property("raw_report_seconds", perf_counter() - started)
    assert raw.status_code == 200
    assert raw.json()["summary"]["totalRequests"] == 29700
    async with SessionLocal() as session:
        while await fold_next_report_slice(session, datetime(2026, 7, 1)):
            pass
        await session.execute(delete(RequestLog))
        await session.commit()
    app_instance.state.reports_caches = ReportsCaches()
    started = perf_counter()
    folded = await async_client.get("/api/reports", params=params)
    record_property("folded_report_seconds", perf_counter() - started)
    assert folded.status_code == 200
    assert folded.json()["summary"] == raw.json()["summary"]
    assert folded.json()["daily"] == raw.json()["daily"]


async def seed_upstreams() -> None:
    async with SessionLocal() as session:
        session.add_all(
            [
                ModelSource(id="src-a", name="Same name", kind="openai_compatible", base_url="https://secret-a.test"),
                ModelSource(id="src-b", name="Same name", kind="openai_compatible", base_url="https://secret-b.test"),
            ]
        )
        for i, (source, key, status, deleted) in enumerate(
            [
                (None, "k1", "error", False),
                (None, "k2", "success", False),
                ("src-a", "k1", "success", False),
                ("src-a", "k2", "error", False),
                ("src-b", "k2", "success", False),
                ("src-gone", "k1", "success", False),
                ("src-hidden", "k1", "success", True),
            ]
        ):
            session.add(
                RequestLog(
                    request_id=f"upstream-{i}",
                    model="same-model",
                    model_source_id=source,
                    model_source_kind="openai_compatible" if source else None,
                    api_key_id=key,
                    status=status,
                    requested_at=NOW.replace(tzinfo=None),
                    deleted_at=NOW.replace(tzinfo=None) if deleted else None,
                )
            )
        await session.commit()


@pytest.mark.parametrize("path", ["/api/request-logs", "/api/request-logs/"])
@pytest.mark.parametrize(
    "selected,expected",
    [
        (["subscription_pool"], {"upstream-0", "upstream-1"}),
        (["src-a"], {"upstream-2", "upstream-3"}),
        (["src-gone"], {"upstream-5"}),
        (["subscription_pool", "src-b"], {"upstream-0", "upstream-1", "upstream-4"}),
        (["missing"], set()),
    ],
)
async def test_upstream_api_or_filter_and_exact_total(async_client, db_setup, path, selected, expected):
    await seed_upstreams()
    response = await async_client.get(path, params=[("upstream", value) for value in selected])
    assert response.status_code == 200
    body = response.json()
    assert {row["requestId"] for row in body["requests"]} == expected
    assert body["total"] == len(expected)


async def test_upstream_and_filters_cache_isolation_and_no_demand_rollup(async_client, db_setup, monkeypatch):
    await seed_upstreams()
    monkeypatch.setattr(logs_module, "_COUNT_CACHE_TTL_SECONDS", 60)
    logs_module._clear_recent_count_cache()

    async def forbidden(*args, **kwargs):
        pytest.fail("source-filtered count consulted a rollup without the source dimension")

    monkeypatch.setattr(logs_module.RequestLogsRepository, "_count_recent_from_demand_rollup", forbidden)
    try:
        for upstream, key, total in [("src-a", "k1", 1), ("src-b", "k1", 0), ("src-a", "k2", 0)]:
            response = await async_client.get(
                "/api/request-logs",
                params={
                    "upstream": upstream,
                    "apiKeyId": key,
                    "model": "same-model",
                    "status": "ok",
                },
            )
            assert response.status_code == 200
            assert response.json()["total"] == total
    finally:
        logs_module._clear_recent_count_cache()


@pytest.mark.parametrize("path", ["/api/request-logs/options", "/api/request-logs/options/"])
async def test_upstream_options_self_exemption_deletion_and_cross_facet(async_client, db_setup, path):
    await seed_upstreams()
    response = await async_client.get(path, params={"upstream": "src-a"})
    assert response.status_code == 200
    body = response.json()
    assert {option["id"] for option in body["upstreams"]} == {"subscription_pool", "src-a", "src-b", "src-gone"}
    gone = next(option for option in body["upstreams"] if option["id"] == "src-gone")
    assert gone == {
        "id": "src-gone",
        "type": "model_source",
        "displayName": None,
        "modelSourceKind": "openai_compatible",
        "isDeleted": True,
    }
    assert "secret-" not in response.text
    assert {option["id"] for option in body["apiKeys"]} == {"k1", "k2"}
    filtered = await async_client.get(path, params={"upstream": "src-b", "apiKeyId": "k1", "status": "ok"})
    assert {option["id"] for option in filtered.json()["upstreams"]} == {"src-a", "src-gone"}
    assert filtered.json()["modelOptions"] == []


async def test_upstream_unfiltered_skip_scan_and_renamed_source(async_client, db_setup):
    await seed_upstreams()
    statements = []

    def capture(conn, cursor, statement, parameters, context, executemany):
        statements.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await async_client.get("/api/request-logs/options")
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert response.status_code == 200
    assert any("facet_skip" in sql and "model_source_id" in sql for sql in statements)
    async with SessionLocal() as session:
        source = await session.get(ModelSource, "src-a")
        assert source is not None
        source.name = "Renamed"
        await session.commit()
    renamed = await async_client.get("/api/request-logs/options")
    assert next(o for o in renamed.json()["upstreams"] if o["id"] == "src-a")["displayName"] == "Renamed"


@pytest.mark.parametrize("fold", [False, True])
async def test_activity_utc_calendar_rollup_tail_and_warmup(async_client, db_setup, monkeypatch, fold):
    monkeypatch.setattr(dashboard_api, "utcnow", lambda: NOW, raising=False)
    async with SessionLocal() as session:
        for i, (at, kind) in enumerate(
            [
                (datetime(2026, 4, 30, 23, 59), "normal"),
                (datetime(2026, 5, 1), "normal"),
                (datetime(2026, 5, 1, 0, 20), "warmup"),
                (datetime(2026, 10, 13, 23, 59), "normal"),
                (datetime(2026, 10, 14), "normal"),
                (datetime(2026, 10, 14, 13, 59), "normal"),
                (datetime(2026, 10, 14, 14), "limit_warmup"),
                (datetime(2026, 10, 15), "normal"),
            ]
        ):
            session.add(
                RequestLog(
                    request_id=f"activity-{i}", model="test", status="success", requested_at=at, request_kind=kind
                )
            )
        await session.commit()
    if fold:
        await run_hourly_fold_pass(now=datetime(2026, 10, 14, 13))
        # Remove folded history; the visible aggregate must survive raw retention.
        async with SessionLocal() as session:
            await session.execute(delete(RequestLog).where(RequestLog.requested_at < datetime(2026, 10, 14, 12)))
            await session.commit()
    response = await async_client.get("/api/dashboard/request-activity")
    assert response.status_code == 200
    assert response.json() == {
        "startDate": "2026-05-01",
        "endDate": "2026-10-14",
        "days": [
            {"date": "2026-05-01", "requests": 1},
            {"date": "2026-10-13", "requests": 1},
            {"date": "2026-10-14", "requests": 2},
        ],
    }


async def test_activity_requires_account_read_permission(async_client, app_instance, monkeypatch):
    principal = DashboardPrincipal(
        role=DashboardRole.GUEST, permissions=frozenset(), auth_mode=DashboardAuthMode.STANDARD, grants={}
    )

    async def no_grants(request):
        return principal

    monkeypatch.setattr(auth_dependencies, "validate_dashboard_session", no_grants)
    app_instance.dependency_overrides[validate_dashboard_session] = lambda: principal
    try:
        response = await async_client.get("/api/dashboard/request-activity")
    finally:
        app_instance.dependency_overrides.pop(validate_dashboard_session, None)
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "permission_required"


async def test_upstream_facet_and_list_use_equivalent_offset_bounds(async_client, db_setup):
    await seed_upstreams()
    params = {"since": "2026-10-14T16:00:00+03:00", "until": "2026-10-14T18:00:00+03:00", "upstream": "src-a"}
    listed = await async_client.get("/api/request-logs", params=params)
    options = await async_client.get("/api/request-logs/options", params=params)
    assert listed.status_code == options.status_code == 200
    assert listed.json()["total"] == 2
    assert options.json()["modelOptions"] == [{"model": "same-model", "reasoningEffort": None}]
    assert {o["id"] for o in options.json()["upstreams"]} == {"subscription_pool", "src-a", "src-b", "src-gone"}
