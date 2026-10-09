from __future__ import annotations

import importlib
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from alembic import command
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, event, insert, inspect, text

from app.db import migrate
from app.db.models import RequestLog
from app.db.session import SessionLocal, engine
from app.modules.request_logs.repository import RequestLogsRepository

pytestmark = pytest.mark.integration


@pytest.mark.parametrize(
    "parent", ["20260914_000000_add_scim_tokens", "20260914_000000_drop_subscription_overflow_schema"]
)
def test_populated_scim_overflow_parents_round_trip_and_reach_current_head(tmp_path: Path, parent: str) -> None:
    path = tmp_path / "merge.sqlite"
    url = f"sqlite+aiosqlite:///{path}"
    merge = "20260918_000000_merge_scim_and_overflow_heads"
    parents = {"20260914_000000_add_scim_tokens", "20260914_000000_drop_subscription_overflow_schema"}
    config = migrate._build_alembic_config(url)
    graph = ScriptDirectory.from_config(config)
    heads = graph.get_heads()
    assert len(heads) == 1
    merge_parents = graph.get_revision(merge).down_revision
    assert isinstance(merge_parents, tuple)
    assert set(merge_parents) == parents
    assert merge in {revision.revision for revision in graph.walk_revisions(base="base", head=heads[0])}
    migrate.run_upgrade(url, parent, bootstrap_legacy=False)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "INSERT INTO request_logs (request_id, requested_at, model, status) "
            "VALUES ('keep', '2026-09-01 12:34:56', 'gpt-6-astra', 'success')"
        )
        if parent.endswith("add_scim_tokens"):
            connection.execute(
                "INSERT INTO dashboard_scim_tokens (id, label, token_hash, token_prefix, provider_key) "
                "VALUES (?, ?, ?, ?, ?)",
                ("keep-token", "fixture", "d" * 64, "fixture", "fixture-provider"),
            )
    assert migrate.run_upgrade(url, merge, bootstrap_legacy=False).current_revision == merge
    with sqlite3.connect(path) as connection:
        schema = tuple(connection.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name"))
        assert connection.execute("SELECT request_id FROM request_logs").fetchall() == [("keep",)]
    command.downgrade(config, parent)
    with sqlite3.connect(path) as connection:
        assert {row[0] for row in connection.execute("SELECT version_num FROM alembic_version")} == parents
        assert (
            tuple(connection.execute("SELECT name, sql FROM sqlite_master WHERE type='table' ORDER BY name")) == schema
        )
    assert migrate.run_upgrade(url, merge, bootstrap_legacy=False).current_revision == merge
    assert migrate.run_upgrade(url, "head", bootstrap_legacy=False).current_revision == heads[0]
    assert not migrate.check_migration_policy(url)
    assert not migrate.check_schema_drift(url)
    with sqlite3.connect(path) as connection:
        assert connection.execute("SELECT request_id FROM request_logs").fetchall() == [("keep",)]
        if parent.endswith("add_scim_tokens"):
            assert connection.execute(
                "SELECT provider_key FROM dashboard_scim_tokens WHERE id='keep-token'"
            ).fetchone() == ("fixture-provider",)


def test_facet_indexes_idempotent_and_round_trip_keep_rows(tmp_path: Path) -> None:
    path = tmp_path / "indexes.sqlite"
    url = f"sqlite+aiosqlite:///{path}"
    revision = "20260928_020000_add_request_logs_facet_indexes"
    config = migrate._build_alembic_config(url)
    graph = ScriptDirectory.from_config(config)
    parent = graph.get_revision(revision).down_revision
    assert isinstance(parent, str)
    migrate.run_upgrade(url, parent, bootstrap_legacy=False)
    with sqlite3.connect(path) as connection:
        connection.execute(
            "INSERT INTO request_logs (request_id, requested_at, model, status) "
            "VALUES ('keep', '2026-09-01', 'fixture', 'success')"
        )
    migrate.run_upgrade(url, revision, bootstrap_legacy=False)
    module = importlib.import_module(f"app.db.alembic.versions.{revision}")
    sync_engine = create_engine(f"sqlite:///{path}")
    try:
        with sync_engine.begin() as connection:
            with Operations.context(MigrationContext.configure(connection)):
                module.upgrade()
            indexes = {
                index["name"]: index["column_names"] for index in inspect(connection).get_indexes("request_logs")
            }
            assert indexes["idx_logs_facet_accounts"] == ["deleted_at", "status", "account_id"]
            assert indexes["idx_logs_min_requested"] == ["deleted_at", "request_kind", "requested_at"]
            plan = connection.execute(
                text(
                    "EXPLAIN QUERY PLAN SELECT requested_at, request_kind FROM request_logs "
                    "ORDER BY requested_at LIMIT 1"
                )
            ).all()
            assert any("INDEX" in row[3] for row in plan)
            assert not any("TEMP B-TREE" in row[3] for row in plan)
        command.downgrade(config, parent)
        with sync_engine.connect() as connection:
            assert not {"idx_logs_facet_accounts", "idx_logs_min_requested"} & {
                index["name"] for index in inspect(connection).get_indexes("request_logs")
            }
        migrate.run_upgrade(url, revision, bootstrap_legacy=False)
        with sync_engine.connect() as connection:
            assert connection.execute(text("SELECT request_id FROM request_logs")).all() == [("keep",)]
    finally:
        sync_engine.dispose()


@pytest.mark.asyncio
@pytest.mark.parametrize("kind", [None, "responses", "warmup", "limit_warmup"])
@pytest.mark.parametrize("deleted", [False, True])
async def test_earliest_row_probe_matches_filtered_oracle(db_setup: bool, kind: str | None, deleted: bool) -> None:
    del db_setup
    now = datetime(2026, 10, 9, 12, 34, 56)
    statements: list[str] = []

    def capture(_connection, _cursor, statement, _parameters, _context, _many):
        statements.append(statement)

    async with SessionLocal() as session:
        await session.execute(
            insert(RequestLog),
            [
                {
                    "request_id": "first",
                    "requested_at": now,
                    "request_kind": kind,
                    "deleted_at": now if deleted else None,
                    "model": "fixture",
                    "status": "success",
                },
                {
                    "request_id": "later",
                    "requested_at": now + timedelta(seconds=1),
                    "request_kind": "responses",
                    "model": "fixture",
                    "status": "success",
                },
            ],
        )
        await session.commit()
        event.listen(engine.sync_engine, "before_cursor_execute", capture)
        try:
            earliest = await RequestLogsRepository(session).earliest_activity_at()
        finally:
            event.remove(engine.sync_engine, "before_cursor_execute", capture)
        expected = await session.scalar(
            text(
                "SELECT MIN(requested_at) FROM request_logs WHERE request_kind IS NULL "
                "OR request_kind NOT IN ('warmup', 'limit_warmup')"
            )
        )
    assert earliest == datetime.fromisoformat(expected)
    scans = [statement for statement in statements if "min(request_logs.requested_at)" in statement.lower()]
    assert len(scans) == (1 if kind in {"warmup", "limit_warmup"} else 0)
