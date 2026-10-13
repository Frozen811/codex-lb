from __future__ import annotations

from pathlib import Path

import pytest
from alembic import command
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine

from app.db.migrate import _build_alembic_config, check_schema_drift, run_upgrade

pytestmark = pytest.mark.integration
SCIM = "20260914_000000_add_scim_tokens"
OVERFLOW = "20260914_000000_drop_subscription_overflow_schema"
MERGE = "20260918_000000_merge_scim_and_overflow_heads"


def _retained_rows(engine: Engine) -> tuple[tuple[object, ...], ...]:
    with engine.connect() as connection:
        return tuple(
            tuple(row)
            for row in connection.execute(
                text("SELECT request_id, model, status, input_tokens, output_tokens FROM request_logs")
            )
        )


@pytest.mark.parametrize("start", [SCIM, OVERFLOW, "both"])
def test_populated_september_parents_preserve_rows_through_merge_and_head(tmp_path: Path, start: str) -> None:
    url = f"sqlite:///{tmp_path / 'lineage.db'}"
    config = _build_alembic_config(url)
    script = ScriptDirectory.from_config(config)
    assert len(script.get_heads()) == 1
    merge = script.get_revision(MERGE)
    assert merge is not None and isinstance(merge.down_revision, tuple)
    assert set(merge.down_revision) == {SCIM, OVERFLOW}
    run_upgrade(url, SCIM if start == "both" else start, bootstrap_legacy=False)
    if start == "both":
        run_upgrade(url, OVERFLOW, bootstrap_legacy=False)
    engine = create_engine(url)
    try:
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO request_logs(request_id, model, status, input_tokens, output_tokens) "
                    "VALUES ('retained-september-row', 'gpt-6-astra', 'success', 1234, 56)"
                )
            )
        retained = _retained_rows(engine)
        run_upgrade(url, MERGE, bootstrap_legacy=False)
        merged_schema = set(inspect(engine).get_table_names())
        assert "dashboard_scim_tokens" in merged_schema
        assert "model_source_pins" not in merged_schema
        command.downgrade(config, SCIM)
        with engine.connect() as connection:
            assert set(connection.scalars(text("SELECT version_num FROM alembic_version"))) == {SCIM, OVERFLOW}
        assert set(inspect(engine).get_table_names()) == merged_schema
        assert _retained_rows(engine) == retained
        run_upgrade(url, MERGE, bootstrap_legacy=False)
        assert _retained_rows(engine) == retained
        result = run_upgrade(url, "head", bootstrap_legacy=False)
        assert result.current_revision == script.get_current_head()
        assert _retained_rows(engine) == retained
        assert check_schema_drift(url) == ()
    finally:
        engine.dispose()
