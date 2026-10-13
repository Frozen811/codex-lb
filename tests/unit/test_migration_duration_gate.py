from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[2]
CHECKER = ROOT / "scripts/check_migration_durations.py"


@pytest.fixture(scope="module")
def checker() -> ModuleType:
    spec = importlib.util.spec_from_file_location("duration_checker", CHECKER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize(
    "sql",
    [
        "UPDATE request_logs SET model='fixed'",
        "update usage_history set used_percent=0",
        'UPDATE public."additional_usage_history" SET used_percent=0',
        "UPDATE [request_logs] SET model='LIMIT 1'",
        "UPDATE request_logs SET model='fixed' /* LIMIT 1 */",
        "UPDATE request_logs SET model='fixed' WHERE id >= :start_id OR id < :end_id",
    ],
)
def test_unsafe_updates_are_rejected(checker: ModuleType, tmp_path: Path, sql: str) -> None:
    path = tmp_path / "20261010_000000_unsafe.py"
    path.write_text(f"def upgrade():\n    op.execute({sql!r})\n", encoding="utf-8")
    assert checker.analyze_migration_file(path)


def test_indirect_sql_and_qualified_batch_bounds(checker: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "20261010_000000_indirect.py"
    path.write_text(
        'SQL = "UPDATE request_logs SET model=1"\n' + "def upgrade():\n    op.execute(sa.text(SQL))\n",
        encoding="utf-8",
    )
    assert checker.analyze_migration_file(path)
    path.write_text(
        "def upgrade():\n    op.execute('UPDATE request_logs SET model=1 "
        "WHERE request_logs.id >= :start_id AND request_logs.id < :end_id')\n",
        encoding="utf-8",
    )
    assert checker.analyze_migration_file(path) == []


def test_historical_sql_and_documentation_are_not_execution(checker: ModuleType, tmp_path: Path) -> None:
    path = tmp_path / "20261010_000000_documented.py"
    path.write_text('"""UPDATE request_logs SET model=1"""\ndef upgrade():\n    pass\n', encoding="utf-8")
    assert checker.analyze_migration_file(path) == []
    old = tmp_path / "20260101_000000_old.py"
    old.write_text("op.execute('UPDATE request_logs SET model=1')\n", encoding="utf-8")
    assert checker.analyze_migration_file(old) == []


def test_checker_cli_fails_for_unsafe_migration(tmp_path: Path) -> None:
    (tmp_path / "20261010_000000_unsafe.py").write_text("op.execute('UPDATE request_logs SET model=1')\n")
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--versions-dir", str(tmp_path)], capture_output=True, text=True, check=False
    )
    assert result.returncode == 1
    assert "request_logs" in result.stderr


@pytest.mark.parametrize(
    "source",
    [
        "SQL: str = 'UPDATE request_logs SET model=1'\nop.execute(SQL)\n",
        "TABLE = 'request_logs'\nop.execute(f'UPDATE {TABLE} SET model=1')\n",
        "SQL = 'UPDATE request_logs SET model=1'\nop.execute(SQL)\nSQL = 'SELECT 1'\n",
        "op.execute('UPDATE request_logs SET model=1 WHERE NOT (id >= :start_id AND id < :end_id)')\n",
        "op.execute('UPDATE request_logs SET model=1 WHERE EXISTS "
        "(SELECT 1 FROM usage_history WHERE id >= :start_id AND id < :end_id)')\n",
    ],
)
def test_static_resolution_cannot_hide_unsafe_execution(checker: ModuleType, tmp_path: Path, source: str) -> None:
    path = tmp_path / "20261010_000000_dynamic.py"
    path.write_text(source, encoding="utf-8")
    assert checker.analyze_migration_file(path)


def test_benchmark_cannot_report_a_list_as_database_evidence(tmp_path: Path) -> None:
    result = subprocess.run(
        [sys.executable, str(CHECKER), "--versions-dir", str(tmp_path), "--benchmark"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "benchmark duration" not in result.stderr
