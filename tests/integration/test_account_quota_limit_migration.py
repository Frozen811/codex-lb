from __future__ import annotations

import pytest
from alembic import command
from anyio import to_thread
from sqlalchemy import create_engine, text

from app.db.migrate import _build_alembic_config, run_upgrade


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
