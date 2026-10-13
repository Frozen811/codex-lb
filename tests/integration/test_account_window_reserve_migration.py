from __future__ import annotations

import pytest
from alembic import command
from sqlalchemy import create_engine, text

from app.db.migrate import _build_alembic_config, check_schema_drift, run_upgrade

PARENT = "20261009_000000_activate_reset_warmup_threshold"
REVISION = "20261009_010000_add_account_window_reserves"
pytestmark = pytest.mark.integration


def test_window_reserve_migration_preserves_caps_and_replay(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'reserves.db'}"
    run_upgrade(url, PARENT, bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            for account_id, cap in [("positive", 37.5), ("zero", 0), ("disabled", None)]:
                connection.execute(
                    text("""INSERT INTO accounts
                    (id,email,plan_type,access_token_encrypted,refresh_token_encrypted,id_token_encrypted,
                     last_refresh,codex_installation_id,status,quota_limit_percent)
                    VALUES (:id,:email,'pro',X'01',X'02',X'03','2026-10-09','test','active',:cap)"""),
                    {"id": account_id, "email": f"{account_id}@example.invalid", "cap": cap},
                )
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        run_upgrade(url, "head", bootstrap_legacy=False)
        assert check_schema_drift(url) == ()
        with engine.begin() as connection:
            rows = connection.execute(
                text("SELECT id,quota_limit_percent,usage_limit_enabled,usage_limit_percent FROM accounts ORDER BY id")
            ).all()
            assert [tuple(row) for row in rows] == [
                ("disabled", None, 0, None),
                ("positive", 37.5, 1, 37.5),
                ("zero", 0, 0, None),
            ]
            connection.execute(text("UPDATE accounts SET usage_limit_weekly_percent=45 WHERE id='positive'"))
        command.stamp(_build_alembic_config(url), PARENT)
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT usage_limit_weekly_percent FROM accounts WHERE id='positive'")).scalar()
                == 45
            )
        command.downgrade(_build_alembic_config(url), PARENT)
        with engine.connect() as connection:
            rows = connection.execute(
                text("SELECT id,quota_limit_percent,access_token_encrypted FROM accounts ORDER BY id")
            ).all()
            assert [tuple(row) for row in rows] == [
                ("disabled", None, b"\x01"),
                ("positive", 37.5, b"\x01"),
                ("zero", 0, b"\x01"),
            ]
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        run_upgrade(url, "head", bootstrap_legacy=False)
        assert check_schema_drift(url) == ()
    finally:
        engine.dispose()
