from __future__ import annotations

import io
import json
import logging
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest
from alembic import command

from app import cli
from app.codex_sessions_retag import ProviderCount, retag_codex_sessions
from app.db import migrate

pytestmark = pytest.mark.unit


def _session(home: Path, header: bytes, tail: bytes = b"") -> Path:
    path = home / "sessions" / "session.jsonl"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(header + tail)
    return path


def test_retag_preserves_opaque_transcript_and_counts_only_header(tmp_path: Path) -> None:
    header = b'{"type":"session_meta","payload":{"model_provider":"openai","id":"one"}}\r\n'
    tail = b'{"model_provider":"openai","text":"transcript"}\r\n' + b"opaque\xff\x00" * 300_000
    path = _session(tmp_path, header, tail)
    result = retag_codex_sessions(codex_home=tmp_path, source_provider="openai", target_provider="codex-lb")
    assert path.read_bytes().split(b"\n", 1)[1] == tail
    assert result.provider_counts_before == (ProviderCount("openai", 1),)
    assert result.provider_counts_after == (ProviderCount("codex-lb", 1),)
    assert result.backup_path is not None
    assert (result.backup_path / path.relative_to(tmp_path)).read_bytes() == header + tail


@pytest.mark.parametrize(
    "header", [b"{broken}\n", b'{"model_provider":"openai","text":"' + b"x" * 70_000], ids=["malformed", "oversized"]
)
def test_retag_invalid_initial_metadata_fails_before_backup(tmp_path: Path, header: bytes) -> None:
    path = _session(tmp_path, header)
    with pytest.raises(ValueError, match="metadata"):
        retag_codex_sessions(codex_home=tmp_path, source_provider="openai", target_provider="codex-lb")
    assert path.read_bytes() == header
    assert not (tmp_path / "backups").exists()


def test_retag_cli_exposes_json_progress() -> None:
    args = cli._parse_args(["codex-sessions", "retag", "--from", "openai", "--to", "codex-lb", "--progress-json"])
    assert args.progress_json is True


def test_unknown_revision_failure_explains_guarded_recovery_without_writes(tmp_path: Path) -> None:
    path = tmp_path / "unknown.sqlite"
    with sqlite3.connect(path) as connection:
        connection.execute("CREATE TABLE alembic_version (version_num TEXT PRIMARY KEY)")
        connection.execute("INSERT INTO alembic_version VALUES ('future_unknown_revision')")
        connection.execute("CREATE TABLE keep (value TEXT)")
        connection.execute("INSERT INTO keep VALUES ('unchanged')")
    before = path.read_bytes()
    url = f"sqlite+aiosqlite:///{path}"
    with pytest.raises(migrate.MigrationBootstrapError) as failure:
        migrate.run_upgrade(url, bootstrap_legacy=False)
    message = str(failure.value)
    for text in (
        "schema and data compatibility",
        "migration transactions",
        "backup and encryption key",
        "both",
        "same database",
        "only changes migration metadata",
        "does not roll back schema or data",
    ):
        assert text in message
    assert path.read_bytes() == before
    with pytest.raises(Exception, match="future_unknown_revision"):
        migrate.stamp_revision(url, "future_unknown_revision")
    assert path.read_bytes() == before


def test_online_revision_progress_success_downgrade_and_noop(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'progress.sqlite'}"
    revision = "20260213_000000_base_schema"
    caplog.set_level(logging.INFO, logger="app.db.migration_progress")
    migrate.run_upgrade(url, revision, bootstrap_legacy=False)
    messages = [r.getMessage() for r in caplog.records if r.name == "app.db.migration_progress"]
    assert any(f"Migration started revision={revision} direction=upgrade" in m for m in messages)
    assert any(f"Migration executed revision={revision} direction=upgrade elapsed_seconds=" in m for m in messages)
    caplog.clear()
    migrate.run_upgrade(url, revision, bootstrap_legacy=False)
    assert not [r for r in caplog.records if r.name == "app.db.migration_progress"]
    command.downgrade(migrate._build_alembic_config(url), "base")
    assert any(f"revision={revision} direction=downgrade" in r.getMessage() for r in caplog.records)


def test_migration_cli_progress_stays_on_stderr(tmp_path: Path) -> None:
    url = f"sqlite+aiosqlite:///{tmp_path / 'cli.sqlite'}"
    output = subprocess.run(
        [sys.executable, "-m", "app.db.migrate", "--db-url", url, "upgrade", "20260213_000000_base_schema"],
        capture_output=True,
        text=True,
        check=True,
        timeout=30,
    )
    assert output.stdout == "current_revision=20260213_000000_base_schema\n"
    assert "Migration started revision=" in output.stderr


def test_retag_cli_json_progress_and_summary(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n')
    args = cli._parse_args(
        [
            "codex-sessions",
            "retag",
            "--from",
            "openai",
            "--to",
            "codex-lb",
            "--codex-home",
            str(tmp_path),
            "--yes",
            "--progress-json",
        ]
    )
    cli._run_codex_sessions_retag(args)
    output = capsys.readouterr()
    events = [json.loads(line) for line in output.err.splitlines()]
    assert {e["phase"] for e in events} == {"discovery", "backup", "rewrite", "verification", "complete"}
    assert events[-1]["completed"] == events[-1]["total"] == 1
    assert "Updated JSONL files: 1" in output.out


def test_retag_dry_run_has_one_grouped_count_and_bounded_reads(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import codex_sessions_retag as retag_module

    path = _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n', b"opaque" * 400_000)
    db = tmp_path / "state_5.sqlite"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, model_provider TEXT)")
        connection.executemany("INSERT INTO threads VALUES (?, ?)", [("one", "openai"), ("two", "codex-lb")])
    queries: list[str] = []
    original_connect = retag_module._connect_sqlite

    def connect(*args, **kwargs):
        connection = original_connect(*args, **kwargs)
        connection.set_trace_callback(queries.append)
        return connection

    original_open = Path.open
    reads: list[int] = []

    class Reader:
        def __init__(self, handle):
            self.handle = handle

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.handle.close()

        def read(self, size: int) -> bytes:
            data = self.handle.read(size)
            reads.append(len(data))
            return data

    def open_file(self, *args, **kwargs):
        handle = original_open(self, *args, **kwargs)
        return Reader(handle) if self == path else handle

    monkeypatch.setattr(retag_module, "_connect_sqlite", connect)
    monkeypatch.setattr(Path, "open", open_file)
    result = retag_codex_sessions(
        codex_home=tmp_path, source_provider="openai", target_provider="codex-lb", dry_run=True
    )
    assert reads == [64 * 1024]
    assert [q for q in queries if "COUNT(" in q] == [
        "SELECT model_provider, COUNT(*) FROM threads GROUP BY model_provider"
    ]
    assert result.sqlite_rows_matched == 1
    assert result.provider_counts_before == (ProviderCount("codex-lb", 1), ProviderCount("openai", 2))
    assert result.provider_counts_after == result.provider_counts_before
    assert not (tmp_path / "backups").exists()


@pytest.mark.parametrize("phase", ["discovery", "backup", "rewrite", "verification", "complete"])
def test_retag_closed_progress_during_each_phase_finishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, phase: str
) -> None:
    path = _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n')

    class ClosedReader(io.StringIO):
        def write(self, value: str) -> int:
            if value.startswith("{") and json.loads(value)["phase"] == phase:
                raise BrokenPipeError("closed progress reader")
            return super().write(value)

    monkeypatch.setattr(sys, "stderr", ClosedReader())
    args = cli._parse_args(
        [
            "codex-sessions",
            "retag",
            "--from",
            "openai",
            "--to",
            "codex-lb",
            "--codex-home",
            str(tmp_path),
            "--yes",
            "--progress-json",
        ]
    )
    try:
        cli._run_codex_sessions_retag(args)
        assert json.loads(path.read_bytes())["model_provider"] == "codex-lb"
    finally:
        sys.stderr.close()


def test_retag_partial_write_failure_reports_original_backup(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import codex_sessions_retag as retag_module

    original = b'{"model_provider":"openai","id":"one"}\n'
    path = _session(tmp_path, original)
    second = path.with_name("second.jsonl")
    second.write_bytes(original)
    rewrite = retag_module._retag_jsonl_file

    def fail_second(file, *args, **kwargs):
        if file == path:
            raise OSError("simulated second write failure")
        return rewrite(file, *args, **kwargs)

    monkeypatch.setattr(retag_module, "_retag_jsonl_file", fail_second)
    with pytest.raises(ValueError, match="Backup retained at .*changes may be partial"):
        retag_codex_sessions(codex_home=tmp_path, source_provider="openai", target_provider="codex-lb")
    backup = next((tmp_path / "backups" / "provider-retag").iterdir())
    assert (backup / "sessions" / "second.jsonl").read_bytes() == original
    assert (backup / "sessions" / "session.jsonl").read_bytes() == original
    assert json.loads(second.read_bytes())["model_provider"] == "codex-lb"
    assert path.read_bytes() == original


def test_online_progress_failure_is_private_and_restores_context(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    from alembic.operations import Operations
    from alembic.runtime.migration import MigrationContext, RevisionStep
    from alembic.script import ScriptDirectory
    from sqlalchemy import create_engine

    from app.db.migration_progress import revision_progress

    url = f"sqlite:///{tmp_path / 'failure.sqlite'}"
    script = ScriptDirectory.from_config(migrate._build_alembic_config(url))
    base = script.get_revision("20260213_000000_base_schema")
    step = RevisionStep.upgrade_from_script(script.revision_map, base)
    next_step = RevisionStep.upgrade_from_script(script.revision_map, base)
    failure = RuntimeError("SQL=password private://url")
    executed: list[str] = []
    caplog.set_level(logging.INFO, logger="app.db.migration_progress")

    def fail(**_kwargs):
        assert any("Migration started revision=" in r.getMessage() for r in caplog.records)
        executed.append("failed")
        raise failure

    step.migration_fn = fail
    next_step.migration_fn = lambda **_kwargs: executed.append("later")
    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            context = MigrationContext.configure(connection, opts={"fn": lambda _heads, _context: [step, next_step]})
            original = context._migrations_fn
            with Operations.context(context), pytest.raises(RuntimeError) as caught:
                with revision_progress(context):
                    context.run_migrations()
            assert caught.value is failure
            assert context._migrations_fn is original
    finally:
        engine.dispose()
    assert executed == ["failed"]
    messages = [r.getMessage() for r in caplog.records if r.name == "app.db.migration_progress"]
    assert len(messages) == 2
    assert "Migration failed revision=" in messages[-1]
    assert "elapsed_seconds=" in messages[-1]
    assert not any(word in " ".join(messages) for word in ("password", "private://url", "SQL=", "Migration executed"))


def test_retag_subprocess_with_closed_stderr_pipe_exits_successfully(tmp_path: Path) -> None:
    path = _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n')
    with subprocess.Popen(
        [
            sys.executable,
            "-m",
            "app.cli",
            "codex-sessions",
            "retag",
            "--from",
            "openai",
            "--to",
            "codex-lb",
            "--codex-home",
            str(tmp_path),
            "--yes",
            "--progress-json",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as process:
        assert process.stderr is not None
        process.stderr.close()
        process.stderr = None
        output, _ = process.communicate(timeout=30)
        assert process.returncode == 0, output
    assert json.loads(path.read_bytes())["model_provider"] == "codex-lb"


def test_retag_legacy_large_incomplete_tail_is_preserved(tmp_path: Path) -> None:
    tail = b'{"text":"' + b"x" * 200_000
    path = _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n', tail)
    retag_codex_sessions(codex_home=tmp_path, source_provider="openai", target_provider="codex-lb")
    assert path.read_bytes().split(b"\n", 1)[1] == tail


def test_retag_single_session_refuses_database_without_identity(tmp_path: Path) -> None:
    path = _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n')
    db = tmp_path / "state_5.sqlite"
    with sqlite3.connect(db) as connection:
        connection.execute("CREATE TABLE threads (model_provider TEXT)")
        connection.execute("INSERT INTO threads VALUES ('openai')")
    before = db.read_bytes()
    with pytest.raises(ValueError, match="without an id or thread_id"):
        retag_codex_sessions(
            codex_home=tmp_path, source_provider="openai", target_provider="codex-lb", session_id="one"
        )
    assert db.read_bytes() == before
    assert json.loads(path.read_bytes())["model_provider"] == "openai"
    assert not (tmp_path / "backups").exists()


def test_retag_backup_copy_failure_happens_before_mutation(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from app import codex_sessions_retag as retag_module

    original = b'{"model_provider":"openai","id":"one"}\n'
    path = _session(tmp_path, original)

    def fail(*_args, **_kwargs):
        raise OSError("backup unavailable")

    monkeypatch.setattr(retag_module.os, "link", fail)
    monkeypatch.setattr(retag_module.shutil, "copy2", fail)
    with pytest.raises(ValueError, match="Backup failed before mutation.*Partial backup retained"):
        retag_codex_sessions(codex_home=tmp_path, source_provider="openai", target_provider="codex-lb")
    assert path.read_bytes() == original


def test_retag_does_not_swallow_other_progress_io_failures(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import errno

    path = _session(tmp_path, b'{"model_provider":"openai","id":"one"}\n')

    class Denied(io.StringIO):
        def write(self, _value: str) -> int:
            raise PermissionError(errno.EACCES, "progress denied")

    monkeypatch.setattr(sys, "stderr", Denied())
    args = cli._parse_args(
        [
            "codex-sessions",
            "retag",
            "--from",
            "openai",
            "--to",
            "codex-lb",
            "--codex-home",
            str(tmp_path),
            "--yes",
            "--progress-json",
        ]
    )
    with pytest.raises(SystemExit, match="progress denied"):
        cli._run_codex_sessions_retag(args)
    assert json.loads(path.read_bytes())["model_provider"] == "openai"
    assert not (tmp_path / "backups").exists()
