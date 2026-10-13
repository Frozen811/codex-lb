from __future__ import annotations

import importlib
from types import SimpleNamespace

import pytest
from alembic import command
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects import mysql, postgresql, sqlite
from sqlalchemy.schema import CreateColumn

from app.db.migrate import _build_alembic_config, check_schema_drift, run_upgrade

PARENT = "20261007_000000_add_account_quota_limit"
REVISION = "20261009_000000_activate_reset_warmup_threshold"
pytestmark = pytest.mark.integration


def test_threshold_migration_preserves_legacy_values_and_reupgrade(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'threshold.db'}"
    run_upgrade(url, PARENT, bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            connection.execute(
                text("UPDATE dashboard_settings SET limit_warmup_exhausted_threshold_percent=77 WHERE id=1")
            )
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        run_upgrade(url, "head", bootstrap_legacy=False)
        assert check_schema_drift(url) == ()
        with engine.begin() as connection:
            values = connection.execute(
                text(
                    "SELECT limit_warmup_exhausted_threshold_percent, "
                    "limit_warmup_reset_threshold_percent FROM dashboard_settings"
                )
            ).one()
            assert tuple(values) == (77, 0)
            connection.execute(text("UPDATE dashboard_settings SET limit_warmup_reset_threshold_percent=50"))
        command.downgrade(_build_alembic_config(url), PARENT)
        assert "limit_warmup_reset_threshold_percent" not in {
            column["name"] for column in inspect(engine).get_columns("dashboard_settings")
        }
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        with engine.connect() as connection:
            assert tuple(
                connection.execute(
                    text(
                        "SELECT limit_warmup_exhausted_threshold_percent, "
                        "limit_warmup_reset_threshold_percent FROM dashboard_settings"
                    )
                ).one()
            ) == (77, 0)
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "dialect", [sqlite.dialect(), postgresql.dialect(), mysql.dialect()], ids=["sqlite", "postgresql", "mysql"]
)
def test_threshold_migration_ddl_is_portable(monkeypatch, dialect):
    migration = importlib.import_module(f"app.db.alembic.versions.{REVISION}")
    columns = []
    monkeypatch.setattr(migration.op, "get_bind", lambda: None)
    monkeypatch.setattr(migration.sa, "inspect", lambda _: SimpleNamespace(get_columns=lambda _: []))
    monkeypatch.setattr(migration.op, "add_column", lambda table, column: columns.append((table, column)))
    migration.upgrade()
    [(table, column)] = columns
    ddl = str(CreateColumn(column).compile(dialect=dialect))
    assert table == "dashboard_settings"
    assert "limit_warmup_reset_threshold_percent" in ddl
    assert "DEFAULT 0.0" in ddl.replace("(0.0)", "0.0") and "NOT NULL" in ddl


def test_threshold_migration_rewound_ledger_preserves_active_policy(tmp_path):
    url = f"sqlite+aiosqlite:///{tmp_path / 'threshold-replay.db'}"
    run_upgrade(url, REVISION, bootstrap_legacy=False)
    engine = create_engine(url.replace("+aiosqlite", ""))
    try:
        with engine.begin() as connection:
            connection.execute(text("UPDATE dashboard_settings SET limit_warmup_reset_threshold_percent=50 WHERE id=1"))
        command.stamp(_build_alembic_config(url), PARENT)
        run_upgrade(url, REVISION, bootstrap_legacy=False)
        with engine.connect() as connection:
            assert (
                connection.execute(text("SELECT limit_warmup_reset_threshold_percent FROM dashboard_settings")).scalar()
                == 50
            )
    finally:
        engine.dispose()


@pytest.mark.parametrize(
    "nullable,default,column_type",
    [(True, "0.0", sqlite.REAL()), (False, "99.0", sqlite.REAL()), (False, "0.0", sqlite.INTEGER())],
)
def test_threshold_migration_rejects_incompatible_existing_column(monkeypatch, nullable, default, column_type):
    migration = importlib.import_module(f"app.db.alembic.versions.{REVISION}")
    monkeypatch.setattr(migration.op, "get_bind", lambda: None)
    columns = [
        {"name": "limit_warmup_reset_threshold_percent", "nullable": nullable, "type": column_type, "default": default}
    ]
    monkeypatch.setattr(migration.sa, "inspect", lambda _: SimpleNamespace(get_columns=lambda _: columns))
    with pytest.raises(RuntimeError, match="incompatible schema"):
        migration.upgrade()
