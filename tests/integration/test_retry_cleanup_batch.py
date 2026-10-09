from __future__ import annotations

from collections.abc import Callable

import pytest
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.dml import Delete

from app.db.models import HttpBridgeRetryCircuit
from app.modules.proxy.durable_bridge_repository import DurableBridgeRepository, durable_bridge_hash
from tests.unit.test_durable_bridge_sessions import async_session_factory as _session_factory_fixture

pytestmark = pytest.mark.integration
async_session_factory = _session_factory_fixture


async def _seed(session: AsyncSession, detail: str | None) -> None:
    session.add_all(
        [
            HttpBridgeRetryCircuit(
                session_key_kind="session_header",
                session_key_hash=durable_bridge_hash(key),
                api_key_scope="key-1",
                consecutive_failures=2,
                cooldown_until_epoch=0.0,
                last_detail=detail,
                updated_at_epoch=10.0,
                admission_generation=0,
            )
            for key in ("changed", "unchanged")
        ]
    )
    await session.commit()


@pytest.mark.asyncio
@pytest.mark.parametrize("batch_size", [1, 2])
@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("stream_incomplete", "anchor_superseded"),
        (None, "stream_incomplete"),
        ("stream_incomplete", None),
        ("anchor_superseded", "clean_close"),
    ],
)
async def test_scheduled_cleanup_keeps_detail_changed_after_selection(
    async_session_factory: Callable[[], AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
    batch_size: int,
    before: str | None,
    after: str | None,
) -> None:
    async with async_session_factory() as session:
        await _seed(session, before)
        execute = session.execute
        changed = False
        delete_attempts = 0

        async def execute_with_detail_rewrite(statement, *args, **kwargs):
            nonlocal changed, delete_attempts
            if isinstance(statement, Delete):
                delete_attempts += 1
            if (
                isinstance(statement, Delete)
                and not changed
                and durable_bridge_hash("changed") in statement.compile().params.values()
            ):
                changed = True
                # This candidate has already been selected, even with a
                # one-row batch. Its detail rewrite preserves the other fences.
                await execute(
                    update(HttpBridgeRetryCircuit)
                    .where(HttpBridgeRetryCircuit.session_key_hash == durable_bridge_hash("changed"))
                    .values(last_detail=after)
                )
                await session.commit()
            return await execute(statement, *args, **kwargs)

        monkeypatch.setattr(session, "execute", execute_with_detail_rewrite)
        deleted = await DurableBridgeRepository(session).purge_retry_circuits_before(100_000.0, batch_size=batch_size)
        monkeypatch.setattr(session, "execute", execute)

        remaining = (await session.execute(select(HttpBridgeRetryCircuit))).scalars().all()
        assert changed
        assert deleted == 1
        assert delete_attempts == 2, "a changed candidate must not be selected for deletion again in this pass"
        assert len(remaining) == 1
        assert remaining[0].session_key_hash == durable_bridge_hash("changed")
        assert remaining[0].last_detail == after
        assert remaining[0].updated_at_epoch == 10.0
        assert remaining[0].admission_generation == 0
        assert remaining[0].consecutive_failures == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("batch_size", [1, 2])
@pytest.mark.parametrize("detail", [None, "stream_incomplete", "anchor_superseded"])
async def test_scheduled_cleanup_deletes_unchanged_nullable_detail(
    async_session_factory: Callable[[], AsyncSession], batch_size: int, detail: str | None
) -> None:
    async with async_session_factory() as session:
        await _seed(session, detail)
        assert await DurableBridgeRepository(session).purge_retry_circuits_before(100_000.0, batch_size=batch_size) == 2
        assert (await session.execute(select(HttpBridgeRetryCircuit))).scalars().all() == []


@pytest.mark.asyncio
@pytest.mark.parametrize("batch_size", [1, 2])
@pytest.mark.parametrize(
    ("field", "value"), [("updated_at_epoch", 11.0), ("admission_generation", 1), ("consecutive_failures", 3)]
)
async def test_scheduled_cleanup_preserves_existing_observation_fences(
    async_session_factory: Callable[[], AsyncSession],
    monkeypatch: pytest.MonkeyPatch,
    batch_size: int,
    field: str,
    value: float | int,
) -> None:
    async with async_session_factory() as session:
        await _seed(session, "stream_incomplete")
        execute = session.execute
        changed = False

        async def execute_with_newer_observation(statement, *args, **kwargs):
            nonlocal changed
            if (
                isinstance(statement, Delete)
                and not changed
                and durable_bridge_hash("changed") in statement.compile().params.values()
            ):
                changed = True
                await execute(
                    update(HttpBridgeRetryCircuit)
                    .where(HttpBridgeRetryCircuit.session_key_hash == durable_bridge_hash("changed"))
                    .values(**{field: value})
                )
                await session.commit()
            return await execute(statement, *args, **kwargs)

        monkeypatch.setattr(session, "execute", execute_with_newer_observation)
        assert await DurableBridgeRepository(session).purge_retry_circuits_before(100_000.0, batch_size=batch_size) == 1
        monkeypatch.setattr(session, "execute", execute)
        remaining = (await session.execute(select(HttpBridgeRetryCircuit))).scalars().all()
        assert changed and len(remaining) == 1
        assert remaining[0].session_key_hash == durable_bridge_hash("changed")
        assert remaining[0].last_detail == "stream_incomplete"
        assert remaining[0].updated_at_epoch == (value if field == "updated_at_epoch" else 10.0)
        assert remaining[0].admission_generation == (value if field == "admission_generation" else 0)
        assert remaining[0].consecutive_failures == (value if field == "consecutive_failures" else 2)
