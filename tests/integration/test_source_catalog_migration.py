from __future__ import annotations

import pytest
from alembic import command
from anyio import to_thread
from sqlalchemy import create_engine, text

from app.core.config.settings import get_settings
from app.db.migrate import _build_alembic_config, check_schema_drift, run_upgrade
from app.db.session import SessionLocal

pytestmark = pytest.mark.integration
PARENT = "20261009_010000_add_account_window_reserves"
REVISION = "20261010_000000_add_source_catalog_discovery"

_SOURCE = """INSERT INTO model_sources (id,name,base_url,api_key_encrypted)
VALUES ('historical','historical','https://example.invalid/v1',:secret)"""
_MODEL = """INSERT INTO model_source_models (source_id,model,is_enabled)
VALUES ('historical','historical-model',false)"""


def test_historical_catalog_migration_upgrade_replay_and_rollback(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'catalog.db'}"
    run_upgrade(url, PARENT, bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            connection.execute(text(_SOURCE), {"secret": b"synthetic-preserved-secret"})
            connection.execute(text(_MODEL))
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        with engine.connect() as connection:
            assert tuple(
                connection.execute(
                    text("SELECT catalog_mode,catalog_revision,api_key_encrypted FROM model_sources")
                ).one()
            ) == ("manual", 0, b"synthetic-preserved-secret")
            assert tuple(connection.execute(text("SELECT is_enabled,is_available FROM model_source_models")).one()) == (
                0,
                1,
            )
        run_upgrade(url, "head", bootstrap_legacy=False)
        assert check_schema_drift(url) == ()
        command.stamp(_build_alembic_config(url), PARENT)
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        command.downgrade(_build_alembic_config(url), PARENT)
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT api_key_encrypted FROM model_sources")).scalar()
                == b"synthetic-preserved-secret"
            )
            assert connection.execute(text("SELECT is_enabled FROM model_source_models")).scalar() == 0
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        run_upgrade(url, "head", bootstrap_legacy=False)
        assert check_schema_drift(url) == ()
    finally:
        engine.dispose()


@pytest.mark.asyncio
async def test_server_catalog_migration_backfill_replay_and_rollback(db_setup):
    url = get_settings().database_url
    if not url.startswith(("postgresql+", "mysql+", "mariadb+")):
        pytest.skip("Requires isolated PostgreSQL or MySQL")
    assert await to_thread.run_sync(lambda: check_schema_drift(url)) == ()
    async with SessionLocal() as session:
        await session.execute(text("CREATE TABLE alembic_version (version_num VARCHAR(255) NOT NULL PRIMARY KEY)"))
        await session.commit()
    await to_thread.run_sync(lambda: command.stamp(_build_alembic_config(url), REVISION))
    await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), PARENT))
    async with SessionLocal() as session:
        await session.execute(text(_SOURCE), {"secret": b"synthetic-preserved-secret"})
        await session.execute(text(_MODEL))
        await session.commit()
    await to_thread.run_sync(lambda: run_upgrade(url, REVISION, bootstrap_legacy=False))
    await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=False))
    assert await to_thread.run_sync(lambda: check_schema_drift(url)) == ()
    async with SessionLocal() as session:
        source = (
            await session.execute(text("SELECT catalog_mode,catalog_revision,api_key_encrypted FROM model_sources"))
        ).one()
        model = (await session.execute(text("SELECT is_enabled,is_available FROM model_source_models"))).one()
        assert tuple(source) == ("manual", 0, b"synthetic-preserved-secret")
        assert tuple(map(bool, model)) == (False, True)
    await to_thread.run_sync(lambda: command.stamp(_build_alembic_config(url), PARENT))
    await to_thread.run_sync(lambda: run_upgrade(url, REVISION, bootstrap_legacy=False))
    await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), PARENT))
    await to_thread.run_sync(lambda: run_upgrade(url, REVISION, bootstrap_legacy=False))
    await to_thread.run_sync(lambda: run_upgrade(url, "head", bootstrap_legacy=False))
    assert await to_thread.run_sync(lambda: check_schema_drift(url)) == ()
