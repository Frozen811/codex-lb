from __future__ import annotations

import pytest
from alembic import command
from anyio import to_thread
from sqlalchemy import create_engine, inspect, text

from app.db.migrate import MigrationBootstrapError, _build_alembic_config, run_upgrade


@pytest.mark.integration
@pytest.mark.parametrize(
    "target,missing_ledger", [("head", False), ("+1", False), ("20261007_000000", False), ("head", True)]
)
def test_existing_quota_column_survives_rewound_ledger(tmp_path, target: str, missing_ledger: bool) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'quota-replay.db'}"
    parent = "20260928_020000_add_request_logs_facet_indexes"
    head = "20261007_000000_add_account_quota_limit"
    run_upgrade(url, "head", bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("""INSERT INTO accounts
                (id, email, plan_type, access_token_encrypted, refresh_token_encrypted,
                 id_token_encrypted, last_refresh, codex_installation_id, status, quota_limit_percent)
                VALUES ('retained', 'retained@example.com', 'plus', X'01', X'02', X'03', '2026-10-07',
                        'test-id', 'active', 37.5)""")
            )
        if missing_ledger:
            with engine.begin() as connection:
                connection.execute(text("DROP TABLE alembic_version"))
        else:
            command.stamp(_build_alembic_config(url), parent)
        assert run_upgrade(url, target, bootstrap_legacy=True).current_revision == head
        with engine.connect() as connection:
            assert connection.execute(
                text("SELECT quota_limit_percent, access_token_encrypted FROM accounts WHERE id='retained'")
            ).one() == (37.5, b"\x01")
    finally:
        engine.dispose()


@pytest.mark.integration
def test_quota_recovery_applies_pending_ancestor_indexes(tmp_path) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'quota-ancestors.db'}"
    run_upgrade(url, "head", bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    indexes = {"idx_logs_facet_accounts", "idx_logs_min_requested"}
    try:
        with engine.begin() as connection:
            for name in indexes:
                connection.execute(text(f"DROP INDEX {name}"))
        command.stamp(_build_alembic_config(url), "20260928_010000_widen_account_status_enum")
        run_upgrade(url, "head", bootstrap_legacy=True)
        with engine.connect() as connection:
            assert indexes <= {index["name"] for index in inspect(connection).get_indexes("request_logs")}
    finally:
        engine.dispose()


@pytest.mark.integration
@pytest.mark.parametrize("shape", ["TEXT", "FLOAT NOT NULL", "FLOAT DEFAULT 42"])
def test_incompatible_existing_quota_column_does_not_advance_ledger(tmp_path, shape: str) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'quota-incompatible.db'}"
    parent = "20260928_020000_add_request_logs_facet_indexes"
    run_upgrade(url, parent, bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            connection.execute(text(f"ALTER TABLE accounts ADD COLUMN quota_limit_percent {shape}"))
        with pytest.raises(MigrationBootstrapError, match="incompatible.*quota_limit_percent"):
            run_upgrade(url, "head", bootstrap_legacy=True)
        with engine.connect() as connection:
            assert connection.execute(text("SELECT version_num FROM alembic_version")).scalar_one() == parent
    finally:
        engine.dispose()


@pytest.mark.integration
async def test_quota_limit_migration_upgrade_downgrade_preserves_accounts(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'quota-migration.db'}"
    parent = "20260928_020000_add_request_logs_facet_indexes"
    head = "20261007_000000_add_account_quota_limit"
    await to_thread.run_sync(lambda: run_upgrade(url, parent, bootstrap_legacy=False))
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("""INSERT INTO accounts
                (id, email, plan_type, access_token_encrypted, refresh_token_encrypted,
                 id_token_encrypted, last_refresh,
                 codex_installation_id, status)
                VALUES ('retained', 'retained@example.com', 'plus', X'00', X'00', X'00', '2026-10-07',
                        'test-id', 'active')""")
            )
        await to_thread.run_sync(lambda: run_upgrade(url, head, bootstrap_legacy=False))
        with engine.begin() as connection:
            assert (
                connection.execute(text("SELECT quota_limit_percent FROM accounts WHERE id='retained'")).scalar()
                is None
            )
            connection.execute(text("UPDATE accounts SET quota_limit_percent=50 WHERE id='retained'"))
        await to_thread.run_sync(lambda: command.downgrade(_build_alembic_config(url), parent))
        await to_thread.run_sync(lambda: run_upgrade(url, head, bootstrap_legacy=False))
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT email FROM accounts WHERE id='retained'")).scalar()
                == "retained@example.com"
            )
            assert (
                connection.execute(text("SELECT quota_limit_percent FROM accounts WHERE id='retained'")).scalar()
                is None
            )
    finally:
        engine.dispose()
