"""Execute migration duration budgets on isolated synthetic database fixtures."""

from __future__ import annotations

import argparse
import json
import logging
import math
import os
import subprocess
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import URL, make_url

from app.db.migrate import _build_alembic_config, run_upgrade
from app.db.migration_progress import logger as progress_logger
from app.db.migration_url import to_sync_database_url
from scripts.check_migration_topology import ROOT, base_ref_revisions, graph_heads

DEFAULT_ROWS = 3_000_000
DEFAULT_BUDGET_SECONDS = 30.0


@dataclass(frozen=True)
class RevisionTiming:
    revision: str
    elapsed_seconds: float
    status: str


@dataclass
class BenchmarkReport:
    backend: str
    rows: int
    baseline: str
    budget_seconds: float
    timings: list[RevisionTiming] = field(default_factory=list)
    failure: str | None = None
    failure_phase: str | None = None
    cleanup_complete: bool = False
    fixture_rows_seeded: int = 0
    no_pending_migrations: bool = False

    @property
    def passed(self) -> bool:
        return (
            self.failure is None
            and self.cleanup_complete
            and all(
                timing.status == "executed" and timing.elapsed_seconds <= self.budget_seconds for timing in self.timings
            )
        )


class _TimingHandler(logging.Handler):
    def __init__(self, report: BenchmarkReport) -> None:
        super().__init__()
        self.report = report

    def emit(self, record: logging.LogRecord) -> None:
        if not isinstance(record.args, tuple) or len(record.args) != 3:
            return
        if record.msg not in {
            "Migration executed revision=%s direction=%s elapsed_seconds=%.3f",
            "Migration failed revision=%s direction=%s elapsed_seconds=%.3f",
        }:
            return
        revision, direction, elapsed = record.args
        if direction == "upgrade" and isinstance(revision, str) and isinstance(elapsed, (int, float)):
            self.report.timings.append(
                RevisionTiming(revision, float(elapsed), "failed" if record.levelno >= logging.ERROR else "executed")
            )


def resolve_baseline(base_ref: str) -> str:
    if base_ref == "latest-stable":
        tags = subprocess.run(
            ["git", "tag", "--merged", "HEAD", "--list", "v*"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.splitlines()
        import re

        stable = [tag for tag in tags if re.fullmatch(r"v\d+\.\d+\.\d+", tag)]
        if not stable:
            raise ValueError("No reachable stable release tag")
        base_ref = max(stable, key=lambda tag: tuple(map(int, tag[1:].split("."))))
    revisions = base_ref_revisions(base_ref)
    if revisions is None:
        raise ValueError("Baseline Git ref is unavailable")
    heads = graph_heads(revisions)
    if len(heads) != 1:
        raise ValueError("Baseline must have exactly one migration head")
    return heads[0]


@contextmanager
def disposable_database(backend: str, server_url: str | None) -> Iterator[str]:
    if backend == "sqlite":
        with tempfile.TemporaryDirectory(prefix="codex-migration-duration-") as directory:
            url = URL.create("sqlite", database=str(Path(directory) / "benchmark.db"))
            yield url.render_as_string(hide_password=False)
        return
    if server_url is None:
        raise ValueError("PostgreSQL benchmark server environment variable is missing")
    server = make_url(to_sync_database_url(server_url))
    if server.get_backend_name() != "postgresql":
        raise ValueError("Benchmark server must be PostgreSQL")
    database_name = f"codex_migration_benchmark_{uuid4().hex}"
    admin = create_engine(server, isolation_level="AUTOCOMMIT", connect_args={"connect_timeout": 10})
    try:
        with admin.connect() as connection:
            connection.exec_driver_sql(f'CREATE DATABASE "{database_name}"')
        try:
            benchmark_url = server.set(database=database_name)
            yield benchmark_url.render_as_string(hide_password=False)
        finally:
            with admin.connect() as connection:
                connection.exec_driver_sql(f'DROP DATABASE "{database_name}" WITH (FORCE)')
    finally:
        admin.dispose()


def seed_request_logs(database_url: str, rows: int) -> None:
    """Generate a synthetic mix, using only columns present at the baseline."""
    engine = create_engine(database_url)
    try:
        columns = {column["name"] for column in inspect(engine).get_columns("request_logs")}
        values = {
            "request_id": "'synthetic-' || CAST(i AS TEXT)",
            "model": "CASE WHEN i % 3 = 0 THEN 'gpt-6-sol' ELSE 'gpt-6-astra' END",
            "status": "CASE WHEN i % 10 = 0 THEN 'error' ELSE 'success' END",
            "requested_at": "'2026-09-01 00:00:00'",
            "input_tokens": "1000 + i % 100000",
            "output_tokens": "i % 3000",
            "useragent": "CASE WHEN i % 5 = 0 THEN NULL WHEN i % 2 = 0 THEN 'codex_cli_rs/0.1' ELSE 'Mozilla/5.0' END",
            "useragent_group": "CASE WHEN i % 3 = 0 THEN NULL ELSE 'legacy' END",
            "latency_ms": "100 + i % 10000",
            "cached_input_tokens": "i % 1000",
        }
        selected = {name: value for name, value in values.items() if name in columns}
        projection = f"INSERT INTO request_logs ({', '.join(selected)}) SELECT {', '.join(selected.values())}"
        # Seed batches commit separately; setup timing is excluded from revision execution.
        for start in range(1, rows + 1, 100_000):
            end = min(start + 99_999, rows)
            source = (
                "generate_series(CAST(:start AS INTEGER), CAST(:end AS INTEGER)) AS fixture(i)"
                if engine.dialect.name == "postgresql"
                else "(WITH RECURSIVE fixture(i) AS (SELECT :start UNION ALL SELECT i+1 FROM fixture WHERE i<:end) "
                "SELECT i FROM fixture)"
            )
            with engine.begin() as connection:
                connection.execute(text(f"{projection} FROM {source}"), {"start": start, "end": end})
        with engine.begin() as connection:
            actual = connection.scalar(text("SELECT count(*) FROM request_logs"))
            if actual != rows:
                raise ValueError("Synthetic fixture row count differs from requested scale")
            connection.execute(text("ANALYZE request_logs"))
    finally:
        engine.dispose()


def run_benchmark(
    *, backend: str, rows: int, baseline: str, budget_seconds: float, server_url: str | None = None
) -> BenchmarkReport:
    if rows <= 0 or not math.isfinite(budget_seconds) or budget_seconds <= 0:
        raise ValueError("Fixture rows and finite budget must be positive")
    report = BenchmarkReport(backend, rows, baseline, budget_seconds)
    handler = _TimingHandler(report)
    old_level = progress_logger.level
    phase = "database_setup"
    try:
        with disposable_database(backend, server_url) as database_url:
            try:
                config = _build_alembic_config(database_url)
                from alembic.script import ScriptDirectory

                script = ScriptDirectory.from_config(config)
                pending = tuple(script.iterate_revisions("head", baseline))
                if pending:
                    phase = "baseline_upgrade"
                    run_upgrade(database_url, baseline, bootstrap_legacy=False)
                    phase = "seed"
                    seed_request_logs(database_url, rows)
                    report.fixture_rows_seeded = rows
                    phase = "measured_upgrade"
                    if backend == "postgresql":
                        database_url = (
                            make_url(database_url)
                            .update_query_dict({"options": f"-c statement_timeout={math.ceil(budget_seconds * 1000)}"})
                            .render_as_string(hide_password=False)
                        )
                    progress_logger.setLevel(logging.INFO)
                    progress_logger.addHandler(handler)
                    try:
                        run_upgrade(database_url, "head", bootstrap_legacy=False)
                    finally:
                        progress_logger.removeHandler(handler)
                        progress_logger.setLevel(old_level)
                else:
                    report.no_pending_migrations = True
                if len(report.timings) != len(pending):
                    raise ValueError("Executed migration timing coverage differs from the pending graph")
                if any(t.elapsed_seconds > budget_seconds for t in report.timings):
                    report.failure = "DurationBudgetExceeded"
                    report.failure_phase = phase
            except Exception as exc:
                report.failure = type(exc).__name__
                report.failure_phase = phase
            phase = "cleanup"
        report.cleanup_complete = True
    except Exception as exc:
        # Exception messages may contain credentials, SQL or parameters.
        report.failure = type(exc).__name__
        report.failure_phase = phase
    return report


def write_report(report: BenchmarkReport, output: Path, summary: Path | None) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(asdict(report) | {"passed": report.passed}, indent=2) + "\n", encoding="utf-8")
    if summary is not None:
        lines = [
            "## Synthetic migration duration benchmark",
            "",
            f"Backend: {report.backend}; seeded rows: {report.fixture_rows_seeded}; baseline: {report.baseline}; "
            f"budget: {report.budget_seconds}s.",
            "",
            "| Revision | Elapsed seconds | Status |",
            "| --- | ---: | --- |",
            *[f"| {t.revision} | {t.elapsed_seconds:.6f} | {t.status} |" for t in report.timings],
            "",
            f"Result: {'PASS' if report.passed else 'FAIL'}; failure type: {report.failure or 'none'}.",
            f"No pending migrations: {report.no_pending_migrations}; cleanup complete: {report.cleanup_complete}.",
            "Synthetic measurements do not establish production or hosted CI performance.",
        ]
        with summary.open("a", encoding="utf-8") as stream:
            stream.write("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=("postgresql", "sqlite"), default="postgresql")
    baseline = parser.add_mutually_exclusive_group(required=True)
    baseline.add_argument("--base-ref", help="Git ref or latest-stable (reachable vX.Y.Z tags)")
    baseline.add_argument("--base-revision", help="Explicit baseline Alembic revision")
    parser.add_argument("--rows", type=int, default=DEFAULT_ROWS)
    parser.add_argument("--budget-seconds", type=float, default=DEFAULT_BUDGET_SECONDS)
    parser.add_argument("--server-url-env", default="MIGRATION_BENCHMARK_SERVER_URL")
    parser.add_argument("--output", type=Path, default=Path("migration-duration.json"))
    parser.add_argument("--summary", type=Path)
    args = parser.parse_args()
    if args.rows <= 0 or not math.isfinite(args.budget_seconds) or args.budget_seconds <= 0:
        parser.error("Fixture rows and finite budget must be positive")
    try:
        revision = args.base_revision or resolve_baseline(args.base_ref)
        report = run_benchmark(
            backend=args.backend,
            rows=args.rows,
            baseline=revision,
            budget_seconds=args.budget_seconds,
            server_url=os.environ.get(args.server_url_env),
        )
    except Exception as exc:
        report = BenchmarkReport(args.backend, args.rows, "unresolved", args.budget_seconds, failure=type(exc).__name__)
    write_report(report, args.output, args.summary)
    print(f"Synthetic migration benchmark: {'PASS' if report.passed else 'FAIL'}; report={args.output}")
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
