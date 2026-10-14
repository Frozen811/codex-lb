from __future__ import annotations

import json
from datetime import timedelta

import pytest
from sqlalchemy import select

import app.modules.proxy.service as proxy_module
from app.core.crypto import TokenEncryptor
from app.core.usage import capacity_for_plan, clear_plan_capacity_overrides, set_plan_capacity_override
from app.core.utils.time import naive_utc_to_epoch, utcnow
from app.db.models import Account, AccountStatus, RequestLog, UsageHistory
from app.db.session import SessionLocal
from app.modules.dashboard.repository import DashboardRepository
from app.modules.dashboard.weekly_cost import WeeklyCostWindow

pytestmark = pytest.mark.integration


def _account(account_id: str, plan: str) -> Account:
    encryptor = TokenEncryptor()
    return Account(
        id=account_id,
        email=f"{account_id}@example.invalid",
        plan_type=plan,
        status=AccountStatus.ACTIVE,
        access_token_encrypted=encryptor.encrypt("test-access"),
        refresh_token_encrypted=encryptor.encrypt("test-refresh"),
        id_token_encrypted=encryptor.encrypt("test-id"),
        last_refresh=utcnow(),
    )


@pytest.mark.asyncio
async def test_mixed_pro_pool_uses_independent_weekly_estimates(async_client, db_setup):
    now = utcnow()
    reset_at = int(naive_utc_to_epoch(now + timedelta(days=2)))
    async with SessionLocal() as session:
        session.add_all([_account("lite", "prolite"), _account("pro", "pro")])
        await session.flush()
        session.add_all(
            [
                UsageHistory(
                    account_id=account_id,
                    window="secondary",
                    used_percent=used,
                    recorded_at=now,
                    reset_at=reset_at,
                    window_minutes=10080,
                )
                for account_id, used in [("lite", 0), ("pro", 100)]
            ]
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/overview")
    assert response.status_code == 200, response.text
    body = response.json()
    window = body["summary"]["secondaryWindow"]
    assert window["capacityCredits"] == 45000
    assert window["remainingCredits"] == 9000
    assert window["remainingPercent"] == 20
    assert window["creditsAreEstimates"] is True
    assert all(account["creditsAreEstimates"] for account in body["accounts"])


@pytest.mark.asyncio
async def test_weekly_usd_estimates_match_account_intervals_on_both_endpoints(async_client, db_setup):
    now = utcnow().replace(microsecond=0)
    latest = now - timedelta(seconds=30)
    baseline = latest - timedelta(hours=2)
    async with SessionLocal() as session:
        session.add_all([_account("a", "pro"), _account("b", "prolite")])
        await session.flush()
        for account_id, end_used, cost, reset_days in [("a", 30, 4.0, 2), ("b", 60, 12.0, 4)]:
            reset = int(naive_utc_to_epoch(now + timedelta(days=reset_days)))
            for at, used in [(baseline, end_used - 10), (latest, end_used)]:
                session.add(
                    UsageHistory(
                        account_id=account_id,
                        window="secondary",
                        used_percent=used,
                        recorded_at=at,
                        reset_at=reset,
                        window_minutes=10080,
                    )
                )
            for at, amount, suffix in [
                (baseline + timedelta(hours=1), cost, "matched"),
                (baseline - timedelta(hours=1), 999.0, "outside"),
            ]:
                session.add(
                    RequestLog(
                        account_id=account_id,
                        request_id=f"{account_id}-{suffix}",
                        model="gpt-5.6-luna",
                        status="success",
                        requested_at=at,
                        input_tokens=100,
                        output_tokens=10,
                        cost_usd=amount,
                    )
                )
        await session.commit()
    results = []
    for path in [
        "/api/dashboard/overview?timeframe=1d",
        "/api/dashboard/overview?timeframe=30d",
        "/api/dashboard/projections",
    ]:
        response = await async_client.get(path)
        assert response.status_code == 200, response.text
        pace = response.json()["weeklyCreditPace"]
        assert pace["estimatedFullWeeklyLimitCostUsd"] is None
        assert pace["usedCostUsd"] is None
        estimates = pace["accountCostEstimates"]
        assert {entry["accountId"]: entry["estimatedFullWeeklyLimitCostUsd"] for entry in estimates} == {
            "a": 40.0,
            "b": 120.0,
        }
        assert {entry["observedUsedPercent"] for entry in estimates} == {10.0}
        results.append(estimates)
    assert results[0] == results[1] == results[2]


@pytest.mark.asyncio
async def test_seven_free_monthly_windows_do_not_become_weekly_capacity(async_client, db_setup):
    now = utcnow()
    async with SessionLocal() as session:
        session.add_all([_account(f"free-{i}", "free") for i in range(7)] + [_account("plus", "plus")])
        await session.flush()
        for i in range(7):
            session.add(
                UsageHistory(
                    account_id=f"free-{i}",
                    window="primary",
                    used_percent=0,
                    recorded_at=now,
                    reset_at=int(naive_utc_to_epoch(now + timedelta(days=20))),
                    window_minutes=43200,
                )
            )
        session.add(
            UsageHistory(
                account_id="plus",
                window="secondary",
                used_percent=25,
                recorded_at=now,
                reset_at=int(naive_utc_to_epoch(now + timedelta(days=2))),
                window_minutes=10080,
            )
        )
        await session.commit()
    response = await async_client.get("/api/dashboard/overview")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["summary"]["secondaryWindow"]["capacityCredits"] == capacity_for_plan("plus", "secondary")
    assert body["weeklyCreditPace"]["accountCount"] == 1
    for account in body["accounts"]:
        if account["planType"] == "free":
            assert account["usage"]["monthlyRemainingPercent"] == 100
            assert account["remainingCreditsSecondary"] is None


@pytest.mark.asyncio
async def test_pro_reference_tracks_override_in_api(async_client, db_setup):
    now = utcnow()
    async with SessionLocal() as session:
        session.add(_account("pro", "pro"))
        await session.flush()
        session.add(
            UsageHistory(
                account_id="pro",
                window="secondary",
                used_percent=30,
                recorded_at=now,
                reset_at=int(naive_utc_to_epoch(now + timedelta(days=2))),
                window_minutes=10080,
            )
        )
        await session.commit()
    try:
        set_plan_capacity_override("pro", "secondary", 12000)
        response = await async_client.get("/api/dashboard/projections")
        assert response.status_code == 200, response.text
        pace = response.json()["weeklyCreditPace"]
        assert pace["proWeeklyCapacityCredits"] == 12000
        assert pace["totalFullCredits"] == 12000
        assert capacity_for_plan("pro", "primary") == 1500
    finally:
        clear_plan_capacity_overrides()


@pytest.mark.asyncio
@pytest.mark.parametrize("extra", ["missing_price", "external_source", "deleted"])
async def test_weekly_dollar_estimates_require_complete_subscription_costs(async_client, db_setup, extra):
    now = utcnow().replace(microsecond=0)
    async with SessionLocal() as session:
        session.add(_account("a", "pro"))
        await session.flush()
        for at, used in [(now - timedelta(hours=2), 30), (now, 40)]:
            session.add(
                UsageHistory(
                    account_id="a",
                    window="secondary",
                    used_percent=used,
                    recorded_at=at,
                    window_minutes=10080,
                    reset_at=int(naive_utc_to_epoch(now + timedelta(days=2))),
                )
            )
        for index, cost in enumerate([4.0, None if extra == "missing_price" else 999.0]):
            log = RequestLog(
                account_id="a",
                request_id=f"cost-{index}",
                model="gpt-5.6-luna",
                status="success",
                input_tokens=100,
                output_tokens=10,
                cost_usd=cost,
                requested_at=now - timedelta(hours=1),
            )
            if index == 1 and extra == "external_source":
                log.model_source_id = "external"
                log.model_source_kind = "openai"
            if index == 1 and extra == "deleted":
                log.deleted_at = now
            session.add(log)
        await session.commit()
    for path in ["/api/dashboard/overview", "/api/dashboard/projections"]:
        response = await async_client.get(path)
        assert response.status_code == 200, response.text
        estimates = response.json()["weeklyCreditPace"]["accountCostEstimates"]
        if extra == "missing_price":
            assert estimates == []
        else:
            assert len(estimates) == 1
            assert estimates[0]["estimatedFullWeeklyLimitCostUsd"] == 40


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path", ["/backend-api/codex/responses", "/backend-api/codex/responses/", "/v1/responses", "/v1/responses/"]
)
@pytest.mark.parametrize(
    ("input_tokens", "cached_tokens", "expected_cost"), [(200_000, 100_000, 1.222), (1_000_000, 500_000, 2.02)]
)
async def test_luna_request_paths_record_current_price(
    async_client, db_setup, monkeypatch, path, input_tokens, cached_tokens, expected_cost
):
    async with SessionLocal() as session:
        session.add(_account("luna", "pro"))
        await session.commit()

    async def upstream(payload, headers, access_token, account_id, base_url=None, raise_for_status=False):
        usage = {
            "input_tokens": input_tokens,
            "output_tokens": 1_000_000,
            "input_tokens_details": {"cached_tokens": cached_tokens},
            "output_tokens_details": {"reasoning_tokens": 20_000},
        }
        event = {
            "type": "response.completed",
            "response": {
                "id": "resp-luna",
                "status": "completed",
                "model": "gpt-5.6-luna",
                "output": [],
                "usage": usage,
            },
        }
        yield f"data: {json.dumps(event)}\n\n"

    monkeypatch.setattr(proxy_module, "core_stream_responses", upstream)
    response = await async_client.post(
        path, json={"model": "gpt-5.6-luna", "instructions": "test", "input": [], "stream": True}
    )
    assert response.status_code == 200, response.text
    assert "response.completed" in response.text
    async with SessionLocal() as session:
        log = (await session.execute(select(RequestLog).where(RequestLog.account_id == "luna"))).scalar_one()
        assert log.cost_usd == pytest.approx(expected_cost)
        assert log.reasoning_tokens == 20_000  # Already included in output; never priced twice.


@pytest.mark.asyncio
async def test_weekly_cost_query_batches_more_than_one_hundred_accounts(db_setup):
    now = utcnow()
    async with SessionLocal() as session:
        session.add_all([_account(f"batch-{i}", "pro") for i in range(101)])
        await session.flush()
        session.add_all(
            [
                RequestLog(
                    account_id=f"batch-{i}",
                    request_id=f"batch-{i}",
                    model="gpt-5.6-luna",
                    status="success",
                    requested_at=now - timedelta(minutes=30),
                    cost_usd=4,
                )
                for i in range(101)
            ]
        )
        await session.commit()
        windows = [WeeklyCostWindow(f"batch-{i}", now - timedelta(hours=1), now, 10) for i in range(101)]
        costs = await DashboardRepository(session).weekly_costs(windows)
        assert costs == {f"batch-{i}": 4 for i in range(101)}


@pytest.mark.asyncio
async def test_zero_pro_reference_omits_equivalents_without_losing_other_plan_pace(async_client, db_setup):
    now = utcnow()
    async with SessionLocal() as session:
        session.add(_account("plus", "plus"))
        await session.flush()
        session.add(
            UsageHistory(
                account_id="plus",
                window="secondary",
                used_percent=30,
                recorded_at=now,
                reset_at=int(naive_utc_to_epoch(now + timedelta(days=2))),
                window_minutes=10080,
            )
        )
        await session.commit()
    try:
        set_plan_capacity_override("pro", "secondary", 0)
        response = await async_client.get("/api/dashboard/projections")
        assert response.status_code == 200, response.text
        pace = response.json()["weeklyCreditPace"]
        assert pace["proWeeklyCapacityCredits"] == 0
        assert pace["proAccountEquivalentToCoverOverPlan"] is None
        assert pace["addProAccounts"] is None
    finally:
        clear_plan_capacity_overrides()
