"""backfill request log useragent families

Revision ID: 20260722_000000_backfill_request_log_useragent_families
Revises: 20260720_000000_add_request_log_conversation_id
Create Date: 2026-07-22 00:00:00.000000
"""

from __future__ import annotations

from alembic import op

revision = "20260722_000000_backfill_request_log_useragent_families"
down_revision = "20260720_000000_add_request_log_conversation_id"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect_name = bind.dialect.name
    if dialect_name == "postgresql":
        set_expr = "useragent_group = substring(useragent from 1 for position('/' in useragent) - 1)"
        where_cond = "useragent IS NOT NULL AND position('/' in useragent) > 0 AND useragent_group IS NULL"
    else:
        set_expr = "useragent_group = substr(useragent, 1, instr(useragent, '/') - 1)"
        where_cond = "useragent IS NOT NULL AND instr(useragent, '/') > 0 AND useragent_group IS NULL"

    from app.db.backfill import execute_batched_backfill

    execute_batched_backfill(
        bind=bind,
        table_name="request_logs",
        update_statement=(
            f"UPDATE request_logs SET {set_expr} "
            f"WHERE {where_cond} AND id >= :start_id AND id < :end_id"
        ),
        batch_size=5000,
    )


def downgrade() -> None:
    pass
