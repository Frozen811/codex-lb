"""Non-blocking, resumable, and observable data-backfill helper for migrations."""

from __future__ import annotations

import logging

from sqlalchemy import text
from sqlalchemy.engine import Connection

logger = logging.getLogger(__name__)

DEFAULT_BACKFILL_BATCH_SIZE = 5000


def execute_batched_backfill(
    bind: Connection,
    table_name: str,
    update_statement: str,
    id_column: str = "id",
    batch_size: int = DEFAULT_BACKFILL_BATCH_SIZE,
    log_progress: bool = True,
) -> int:
    """Execute an update backfill in bounded ID-ranged chunks.

    Ensures data migrations:
    1. Are resumable by scoping queries to specific ID ranges and target filters.
    2. Do not hold long-running table-level exclusive locks.
    3. Are observable by logging chunk progress.
    """
    id_bounds = bind.execute(text(f"SELECT min({id_column}), max({id_column}) FROM {table_name}")).first()
    if not id_bounds or id_bounds[0] is None or id_bounds[1] is None:
        return 0

    min_id = int(id_bounds[0])
    max_id = int(id_bounds[1])
    total_affected = 0

    stmt = text(update_statement)
    current_id = min_id

    while current_id <= max_id:
        end_id = current_id + batch_size
        result = bind.execute(stmt, {"start_id": current_id, "end_id": end_id})
        rowcount = result.rowcount if result.rowcount is not None and result.rowcount >= 0 else 0
        total_affected += rowcount

        if log_progress and (current_id == min_id or rowcount > 0 or end_id > max_id):
            logger.info(
                "Backfill progress table=%s id_range=[%d, %d) max_id=%d updated_rows=%d total_updated=%d",
                table_name,
                current_id,
                end_id,
                max_id,
                rowcount,
                total_affected,
            )

        current_id = end_id

    return total_affected
