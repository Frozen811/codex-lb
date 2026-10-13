from __future__ import annotations

import pytest
from alembic import command
from anyio import to_thread
from sqlalchemy import text

from app.core.config.settings import get_settings
from app.db.migrate import _build_alembic_config, check_schema_drift, run_upgrade
from app.db.session import SessionLocal

pytestmark = pytest.mark.integration


async def test_server_reserve_backfill_downgrade_and_replay(db_setup):
    url = get_settings().database_url
    if not url.startswith(("postgresql+", "mysql+", "mariadb+")):
        pytest.skip("Server database smoke requires an isolated PostgreSQL/MySQL database")
    parent = "20261009_000000_activate_reset_warmup_threshold"
    revision = "20261009_010000_add_account_window_reserves"
    # db_setup creates the exact current ORM schema without a migration ledger.
    assert await to_thread.run_sync(lambda: check_schema_drift(url)) == ()
    async with SessionLocal() as session:
        # Production migration tooling expands this beyond Alembic's 32-char default.
        await session.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(255) NOT NULL PRIMARY KEY)"))
        await session.commit()
    await to_thread.run_sync(lambda: command.stamp(_build_alembic_config(url), revision))
    await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), parent))
    async with SessionLocal() as session:
        await session.execute(
            text("""INSERT INTO accounts
            (id,email,plan_type,access_token_encrypted,refresh_token_encrypted,id_token_encrypted,
             last_refresh,codex_installation_id,status,quota_limit_percent)
            VALUES ('reserve-server','reserve@example.invalid','pro',:access,:refresh,:id_token,
                    '2026-10-09','server-smoke','active',37.5)"""),
            {"access": b"test-access", "refresh": b"test-refresh", "id_token": b"test-id"},
        )
        await session.commit()
    await to_thread.run_sync(lambda: run_upgrade(url, revision, bootstrap_legacy=False))
    assert await to_thread.run_sync(lambda: check_schema_drift(url)) == ()
    async with SessionLocal() as session:
        row = (
            await session.execute(
                text("SELECT usage_limit_enabled, usage_limit_percent FROM accounts WHERE id='reserve-server'")
            )
        ).one()
        assert bool(row[0]) and row[1] == 37.5
    await to_thread.run_sync(lambda: command.stamp(_build_alembic_config(url), parent))
    await to_thread.run_sync(lambda: run_upgrade(url, revision, bootstrap_legacy=False))
    await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), parent))
    async with SessionLocal() as session:
        row = (
            await session.execute(
                text("SELECT quota_limit_percent,access_token_encrypted FROM accounts WHERE id='reserve-server'")
            )
        ).one()
        assert tuple(row) == (37.5, b"test-access")
    await to_thread.run_sync(lambda: run_upgrade(url, revision, bootstrap_legacy=False))
