from __future__ import annotations

import logging

import pytest
from sqlalchemy import create_engine, text

from app.db.backfill import execute_batched_backfill


def test_execute_batched_backfill_empty_table() -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE test_items (id INTEGER PRIMARY KEY, status TEXT)"))
        affected = execute_batched_backfill(
            conn,
            table_name="test_items",
            update_statement="UPDATE test_items SET status = 'done' WHERE id >= :start_id AND id < :end_id",
            id_column="id",
            batch_size=10,
        )
        assert affected == 0


def test_execute_batched_backfill_chunks_and_logs(caplog: pytest.LogCaptureFixture) -> None:
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE test_items (id INTEGER PRIMARY KEY, status TEXT, val INTEGER)"))
        # Insert 10 items with ids 1..10
        for i in range(1, 11):
            conn.execute(
                text("INSERT INTO test_items (id, status, val) VALUES (:id, 'pending', :val)"),
                {"id": i, "val": i * 10},
            )

    with caplog.at_level(logging.INFO):
        with engine.begin() as conn:
            stmt = (
                "UPDATE test_items SET status = 'processed' "
                "WHERE id >= :start_id AND id < :end_id AND status = 'pending'"
            )
            affected = execute_batched_backfill(
                conn,
                table_name="test_items",
                update_statement=stmt,
                id_column="id",
                batch_size=3,
                log_progress=True,
            )
            assert affected == 10

            # Verify rows are updated
            rows = conn.execute(text("SELECT count(*) FROM test_items WHERE status = 'processed'")).scalar()
            assert rows == 10

            # Verify resumability: running again with the same condition should update 0 rows
            second_pass = execute_batched_backfill(
                conn,
                table_name="test_items",
                update_statement=stmt,
                id_column="id",
                batch_size=3,
                log_progress=True,
            )
            assert second_pass == 0

    assert any("Backfill progress table=test_items" in record.message for record in caplog.records)
