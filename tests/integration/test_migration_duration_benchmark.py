from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from alembic.runtime.migration import MigrationContext, RevisionStep
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, text

import app.db.migration_progress as migration_progress
import scripts.benchmark_migrations as benchmark
from app.db.migrate import _build_alembic_config

pytestmark = pytest.mark.integration
BASELINE = "20260928_020000_add_request_logs_facet_indexes"


def test_real_fixture_and_pending_revisions_are_measured(monkeypatch: pytest.MonkeyPatch) -> None:
    seed = benchmark.seed_request_logs
    observed: list[int] = []

    def verified_seed(url: str, rows: int) -> None:
        seed(url, rows)
        engine = create_engine(url)
        try:
            with engine.connect() as connection:
                observed.append(connection.scalar(text("SELECT count(*) FROM request_logs")))
                assert connection.scalar(text("SELECT count(*) FROM request_logs WHERE useragent IS NULL")) == 10
                assert connection.scalar(text("SELECT count(*) FROM request_logs WHERE status='error'")) == 5
        finally:
            engine.dispose()

    monkeypatch.setattr(benchmark, "seed_request_logs", verified_seed)
    old_handlers = migration_progress.logger.handlers[:]
    old_level = migration_progress.logger.level
    report = benchmark.run_benchmark(backend="sqlite", rows=50, baseline=BASELINE, budget_seconds=30)
    assert report.passed, report
    assert observed == [50] and report.fixture_rows_seeded == 50
    expected = ScriptDirectory.from_config(_build_alembic_config("sqlite://")).iterate_revisions("head", BASELINE)
    assert {item.revision for item in report.timings} == {step.revision for step in expected}
    assert all(item.elapsed_seconds > 0 and item.status == "executed" for item in report.timings)
    assert report.cleanup_complete and not report.no_pending_migrations
    assert migration_progress.logger.handlers == old_handlers and migration_progress.logger.level == old_level


def test_cli_budget_failure_keeps_json_and_summary(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    summary = tmp_path / "summary.md"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "scripts.benchmark_migrations",
            "--backend",
            "sqlite",
            "--base-revision",
            BASELINE,
            "--rows",
            "20",
            "--budget-seconds",
            "0.000000001",
            "--output",
            str(output),
            "--summary",
            str(summary),
        ],
        cwd=benchmark.ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 1, result.stderr
    report = json.loads(output.read_text())
    assert not report["passed"] and report["timings"]
    assert report["failure"] == "DurationBudgetExceeded" and report["cleanup_complete"]
    assert "FAIL" in summary.read_text() and "Synthetic" in summary.read_text()


def test_actual_failed_revision_retains_private_timing(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    original = migration_progress.revision_progress
    target = "20261007_000000_add_account_quota_limit"

    def failure(**_kwargs: object) -> None:
        raise RuntimeError("private-token SQL secret credentials")

    @contextmanager
    def inject(context: MigrationContext) -> Iterator[None]:
        original_steps = context._migrations_fn
        assert original_steps is not None

        def failed_steps(heads: tuple[str, ...], ctx: MigrationContext) -> Iterator[RevisionStep]:
            for step in original_steps(heads, ctx):
                if isinstance(step, RevisionStep) and step.is_upgrade and step.revision.revision == target:
                    step.migration_fn = failure
                yield step

        context._migrations_fn = failed_steps
        try:
            with original(context):
                yield
        finally:
            context._migrations_fn = original_steps

    monkeypatch.setattr(migration_progress, "revision_progress", inject)
    report = benchmark.run_benchmark(backend="sqlite", rows=20, baseline=BASELINE, budget_seconds=30)
    assert not report.passed and report.failure == "RuntimeError" and report.cleanup_complete
    assert report.failure_phase == "measured_upgrade"
    assert len(report.timings) == 1 and report.timings[0].revision == target and report.timings[0].status == "failed"
    output = tmp_path / "failed.json"
    benchmark.write_report(report, output, tmp_path / "failed.md")
    assert "private-token" not in output.read_text() and "credentials" not in output.read_text()


def test_no_pending_migrations_is_explicit_without_fake_timings(monkeypatch: pytest.MonkeyPatch) -> None:
    head = ScriptDirectory.from_config(_build_alembic_config("sqlite://")).get_current_head()
    assert head is not None
    monkeypatch.setattr(benchmark, "seed_request_logs", lambda *_: pytest.fail("No-op must not seed a fixture"))
    report = benchmark.run_benchmark(backend="sqlite", rows=50, baseline=head, budget_seconds=30)
    assert report.passed and report.no_pending_migrations and report.cleanup_complete
    assert report.timings == [] and report.fixture_rows_seeded == 0


@pytest.mark.parametrize("rows,budget", [(0, 30), (10, 0), (10, float("nan")), (10, float("inf"))])
def test_invalid_scale_or_budget_fails_before_storage(rows: int, budget: float) -> None:
    with pytest.raises(ValueError):
        benchmark.run_benchmark(backend="sqlite", rows=rows, baseline=BASELINE, budget_seconds=budget)


def test_postgres_requires_a_server_and_never_reuses_sqlite(tmp_path: Path) -> None:
    path = tmp_path / "application.db"
    path.write_bytes(b"preserve-existing-database")
    for url in (None, f"sqlite:///{path}"):
        report = benchmark.run_benchmark(
            backend="postgresql", rows=20, baseline=BASELINE, budget_seconds=30, server_url=url
        )
        assert not report.passed and report.failure_phase == "database_setup"
    assert path.read_bytes() == b"preserve-existing-database"


def test_unknown_baseline_fails_with_cleanup_and_private_output(tmp_path: Path) -> None:
    report = benchmark.run_benchmark(backend="sqlite", rows=20, baseline="unknown", budget_seconds=30)
    assert not report.passed and report.cleanup_complete and report.timings == []
    output = tmp_path / "unknown.json"
    benchmark.write_report(report, output, None)
    assert json.loads(output.read_text())["failure"]


def test_baseline_ref_uses_real_git_graph() -> None:
    assert benchmark.resolve_baseline("v1.25.1") == BASELINE
    assert benchmark.resolve_baseline("latest-stable")
    with pytest.raises(ValueError):
        benchmark.resolve_baseline("refs/tags/nonexistent-duration-fixture")
