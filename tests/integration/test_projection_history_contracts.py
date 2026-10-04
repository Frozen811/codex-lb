from __future__ import annotations

from datetime import datetime, timedelta

import pytest
from sqlalchemy import insert

from app.db.models import UsageHistory
from app.db.session import SessionLocal
from app.modules.accounts.repository import AccountsRepository
from app.modules.usage.repository import UsageRepository
from tests.integration.test_usage_repository import _make_account

pytestmark = pytest.mark.integration
BASE = datetime(2026, 9, 20)


@pytest.mark.parametrize("cap", [-1, True, 1.5, "64"])
async def test_projection_history_rejects_invalid_cap(db_setup, cap):
    async with SessionLocal() as session:
        await AccountsRepository(session).upsert(_make_account("cap-validation"))
        await session.execute(
            insert(UsageHistory),
            [
                {
                    "account_id": "cap-validation",
                    "window": "primary",
                    "used_percent": i,
                    "recorded_at": BASE + timedelta(minutes=i),
                }
                for i in range(4)
            ],
        )
        await session.commit()
        with pytest.raises(ValueError, match="per_account_row_cap must be a nonnegative integer"):
            await UsageRepository(session).bulk_history_since(
                ["cap-validation"], "primary", BASE, per_account_row_cap=cap
            )


@pytest.mark.parametrize("window", ["primary", "secondary"])
@pytest.mark.parametrize("cap", [0, 3, 64])
@pytest.mark.parametrize("floor_minutes", [None, 120, -1])
async def test_projection_history_preserves_cap_cutoffs_floor_and_ties(
    db_setup, monkeypatch, window, cap, floor_minutes
):
    import app.modules.usage.repository as module

    def uncapped_read(*args):
        pytest.fail("capped read entered the full-history cache")

    monkeypatch.setattr(module, "_bulk_history_since_sqlite", uncapped_read)
    account_ids = ["history-a", "history-b"]
    cutoffs = {"history-a": BASE + timedelta(minutes=20), "history-b": BASE + timedelta(minutes=124)}
    floor = None if floor_minutes is None else BASE + timedelta(minutes=floor_minutes)
    expected = {}
    async with SessionLocal() as session:
        for account_id in [*account_ids, "unrequested"]:
            await AccountsRepository(session).upsert(_make_account(account_id))
        entries = []
        for account_index, account_id in enumerate([*account_ids, "unrequested"]):
            eligible = []
            for i in range(256):
                recorded_at = BASE + timedelta(minutes=i // 2)
                row_id = 1 + account_index * 256 + i
                entries.append(
                    {
                        "id": row_id,
                        "account_id": account_id,
                        "window": None if window == "primary" and i % 2 else window,
                        "used_percent": i / 3,
                        "recorded_at": recorded_at,
                    }
                )
                if account_id in cutoffs and recorded_at >= cutoffs[account_id]:
                    eligible.append((row_id, recorded_at))
            if account_id in cutoffs:
                recent = [] if floor is None else [row for row in eligible if row[1] >= floor]
                tail = eligible if floor is None else [row for row in eligible if row[1] < floor]
                selected = (tail[-cap:] if cap else []) + recent
                if selected:
                    expected[account_id] = [row[0] for row in selected]
        await session.execute(insert(UsageHistory.__table__), entries)
        await session.commit()
        actual = await UsageRepository(session).bulk_history_since(
            account_ids,
            window,
            BASE,
            cutoffs=cutoffs,
            per_account_row_cap=cap,
            uncapped_recent_floor=floor,
        )
    assert {account_id: [row.id for row in rows] for account_id, rows in actual.items()} == expected


async def test_projection_history_dense_accounts_hydrate_only_capped_tail(db_setup, monkeypatch):
    import app.modules.usage.repository as module

    monkeypatch.setattr(module, "_bulk_history_since_sqlite", lambda *_: pytest.fail("uncapped cache read"))
    account_ids = [f"dense-{i}" for i in range(20)]
    async with SessionLocal() as session:
        for account_id in account_ids:
            await AccountsRepository(session).upsert(_make_account(account_id))
            await session.execute(
                insert(UsageHistory.__table__),
                [
                    {
                        "account_id": account_id,
                        "window": "primary",
                        "used_percent": i / 100,
                        "recorded_at": BASE + timedelta(seconds=i),
                    }
                    for i in range(5000)
                ],
            )
        await session.commit()
        actual = await UsageRepository(session).bulk_history_since(account_ids, "primary", BASE, per_account_row_cap=64)
    assert sum(len(rows) for rows in actual.values()) == 20 * 64
    assert all([row.used_percent for row in rows] == [i / 100 for i in range(4936, 5000)] for rows in actual.values())
