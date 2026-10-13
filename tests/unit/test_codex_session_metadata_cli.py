from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path

import pytest

from app import cli

pytestmark = pytest.mark.unit


@contextmanager
def _db(path: Path) -> Iterator[sqlite3.Connection]:
    with closing(sqlite3.connect(path)) as conn, conn:
        yield conn


def _home(tmp_path: Path, *, jsonl_provider: str = "openai", db_provider: str = "codex-lb") -> Path:
    home = tmp_path / "home"
    session = home / "sessions" / "2026" / "rollout-selected.jsonl"
    session.parent.mkdir(parents=True)
    header = {"type": "session_meta", "payload": {"id": "selected", "model_provider": jsonl_provider}}
    session.write_bytes(json.dumps(header).encode() + b"\n" + b"opaque transcript\xff\r\n")
    (home / "config.toml").write_text('model_provider = "openai"\n', encoding="utf-8")
    (session.parent / "unrelated.jsonl").write_bytes(b"invalid unrelated transcript\xff")
    with _db(home / "state_5.sqlite") as conn:
        conn.execute("CREATE TABLE threads (id TEXT PRIMARY KEY, model_provider TEXT, rollout_path TEXT)")
        conn.executemany(
            "INSERT INTO threads VALUES (?, ?, ?)",
            [("selected", db_provider, str(session)), ("other", "openai", None)],
        )
    return home


def _snapshot(home: Path) -> dict[str, bytes]:
    return {path.relative_to(home).as_posix(): path.read_bytes() for path in home.rglob("*") if path.is_file()}


def _run(home: Path, command: str, *options: str) -> None:
    cli.main(["codex-sessions", command, "--codex-home", str(home), "--session-id", "selected", *options])


def test_preview_json_is_read_only_and_uses_indexed_path(tmp_path, monkeypatch, capsys):
    home = _home(tmp_path)
    before = _snapshot(home)

    def no_traversal(*args, **kwargs):
        raise AssertionError("Indexed repair must not traverse unrelated directories")

    monkeypatch.setattr(Path, "rglob", no_traversal)
    _run(home, "preview", "--json")
    result = json.loads(capsys.readouterr().out)
    assert result["sessions"][0]["status"] == "mismatch"
    assert result["sessions"][0]["jsonl"][0]["provider"] == "openai"
    monkeypatch.undo()
    assert _snapshot(home) == before


def test_confirmed_repair_preserves_tail_config_and_unrelated_session(tmp_path, capsys):
    home = _home(tmp_path)
    before = _snapshot(home)
    _run(home, "repair", "--to", "codex-lb", "--yes", "--json", "--progress-json")
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert result["jsonl_files_updated"] == 1
    assert result["sqlite_rows_updated"] == 0
    backup = Path(result["backup_path"])
    assert (backup / "sessions/2026/rollout-selected.jsonl").read_bytes() == before[
        "sessions/2026/rollout-selected.jsonl"
    ]
    session = home / "sessions/2026/rollout-selected.jsonl"
    header, tail = session.read_bytes().split(b"\n", 1)
    assert json.loads(header)["payload"]["model_provider"] == "codex-lb"
    assert tail == b"opaque transcript\xff\r\n"
    assert (home / "config.toml").read_bytes() == before["config.toml"]
    assert (home / "sessions/2026/unrelated.jsonl").read_bytes() == before["sessions/2026/unrelated.jsonl"]
    with _db(home / "state_5.sqlite") as conn:
        assert conn.execute("SELECT model_provider FROM threads WHERE id='other'").fetchone() == ("openai",)
    phases = [json.loads(line)["phase"] for line in captured.err.splitlines()]
    assert {"backup", "rewrite", "verification", "complete"} <= set(phases)


def test_repair_requires_confirmation_before_writes(tmp_path, monkeypatch):
    home = _home(tmp_path)
    before = _snapshot(home)
    monkeypatch.setattr("sys.stdin.isatty", lambda: False)
    with pytest.raises(SystemExit, match="--yes"):
        _run(home, "repair", "--to", "codex-lb")
    assert _snapshot(home) == before


def test_repair_updates_only_selected_sqlite_row(tmp_path, capsys):
    home = _home(tmp_path, jsonl_provider="codex-lb", db_provider="openai")
    _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    result = json.loads(capsys.readouterr().out)
    assert result["jsonl_files_updated"] == 0
    assert result["sqlite_rows_updated"] == 1
    with _db(home / "state_5.sqlite") as conn:
        assert conn.execute("SELECT id, model_provider FROM threads ORDER BY id").fetchall() == [
            ("other", "openai"),
            ("selected", "codex-lb"),
        ]
    with _db(Path(result["backup_path"]) / "state_5.sqlite") as conn:
        assert conn.execute("SELECT model_provider FROM threads WHERE id='selected'").fetchone() == ("openai",)


@pytest.mark.parametrize("provider", ["other", "", "OPENAI"])
def test_unsupported_provider_is_reported_and_refused(tmp_path, capsys, provider):
    home = _home(tmp_path, jsonl_provider=provider)
    before = _snapshot(home)
    _run(home, "preview", "--json")
    assert json.loads(capsys.readouterr().out)["sessions"][0]["status"] == "unsupported"
    with pytest.raises(SystemExit, match="unsupported"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert _snapshot(home) == before


def test_consistent_repair_is_idempotent_without_backup(tmp_path, capsys):
    home = _home(tmp_path, jsonl_provider="codex-lb")
    before = _snapshot(home)
    _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    result = json.loads(capsys.readouterr().out)
    assert result["backup_path"] is None
    assert result["tags_skipped"] == 2
    assert _snapshot(home) == before


@pytest.mark.parametrize("damage", ["wrong-id", "conflicting-id", "missing-jsonl", "missing-row", "ambiguous-header"])
def test_invalid_targets_refuse_before_backup(tmp_path, damage):
    home = _home(tmp_path)
    session = home / "sessions/2026/rollout-selected.jsonl"
    if damage in {"wrong-id", "conflicting-id", "ambiguous-header"}:
        header = {"type": "session_meta", "payload": {"id": "wrong", "model_provider": "openai"}}
        if damage == "conflicting-id":
            header["id"] = "selected"
        if damage == "ambiguous-header":
            session.write_text(
                json.dumps({"id": "selected", "model_provider": "openai"})
                + "\n"
                + json.dumps({"id": "other", "model_provider": "openai"})
                + "\n",
                encoding="utf-8",
            )
        else:
            session.write_text(json.dumps(header) + "\n", encoding="utf-8")
    elif damage == "missing-jsonl":
        session.unlink()
    else:
        with _db(home / "state_5.sqlite") as conn:
            conn.execute("DELETE FROM threads WHERE id='selected'")
    before = _snapshot(home)
    with pytest.raises(SystemExit):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert _snapshot(home) == before
    assert not (home / "backups").exists()


def test_rollout_outside_home_is_refused(tmp_path):
    home = _home(tmp_path)
    outside = tmp_path / "outside.jsonl"
    outside.write_text('{"id":"selected","model_provider":"openai"}\n', encoding="utf-8")
    with _db(home / "state_5.sqlite") as conn:
        conn.execute("UPDATE threads SET rollout_path=? WHERE id='selected'", (str(outside),))
    before = _snapshot(home)
    with pytest.raises(SystemExit, match="Unsafe"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert _snapshot(home) == before
    assert json.loads(outside.read_text())["model_provider"] == "openai"


def test_stale_plan_after_backup_is_refused_and_keeps_evidence(tmp_path, monkeypatch):
    from app import codex_sessions_repair as repair

    home = _home(tmp_path)
    original = repair._create_backup

    def change_after_backup(*args, **kwargs):
        backup = original(*args, **kwargs)
        with _db(home / "state_5.sqlite") as conn:
            conn.execute("UPDATE threads SET model_provider='other' WHERE id='selected'")
        return backup

    monkeypatch.setattr(repair, "_create_backup", change_after_backup)
    with pytest.raises(SystemExit, match="Backup retained.*changes may be partial"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert list((home / "backups/provider-retag").iterdir())
    header = (home / "sessions/2026/rollout-selected.jsonl").read_bytes().split(b"\n")[0]
    assert json.loads(header)["payload"]["model_provider"] == "openai"


def test_partial_database_failure_keeps_transcript_backup(tmp_path, monkeypatch):
    from app import codex_sessions_repair as repair

    home = _home(tmp_path, db_provider="openai")
    before = _snapshot(home)

    def fail_database(*args, **kwargs):
        raise sqlite3.OperationalError("database is locked")

    monkeypatch.setattr(repair, "_update_sqlite_provider", fail_database)
    with pytest.raises(SystemExit, match="locked.*Backup retained.*changes may be partial"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    backups = list((home / "backups/provider-retag").iterdir())
    assert len(backups) == 1
    assert (backups[0] / "sessions/2026/rollout-selected.jsonl").read_bytes() == before[
        "sessions/2026/rollout-selected.jsonl"
    ]
    with _db(backups[0] / "state_5.sqlite") as conn:
        assert conn.execute("SELECT model_provider FROM threads WHERE id='selected'").fetchone() == ("openai",)


def test_backup_failure_does_not_mutate_metadata(tmp_path, monkeypatch):
    from app import codex_sessions_retag as retag

    home = _home(tmp_path, db_provider="openai")
    before = _snapshot(home)

    def fail_snapshot(*args, **kwargs):
        raise OSError("snapshot failed")

    monkeypatch.setattr(retag, "_backup_sqlite_db", fail_snapshot)
    with pytest.raises(SystemExit, match="Backup failed before mutation"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    after = _snapshot(home)
    assert {path: after[path] for path in before} == before


def test_jsonl_backup_copy_fallback(tmp_path, monkeypatch, capsys):
    from app import codex_sessions_retag as retag

    home = _home(tmp_path)
    before = (home / "sessions/2026/rollout-selected.jsonl").read_bytes()

    def no_hardlinks(*args, **kwargs):
        raise OSError("hard links unavailable")

    monkeypatch.setattr(retag.os, "link", no_hardlinks)
    _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    result = json.loads(capsys.readouterr().out)
    assert (Path(result["backup_path"]) / "sessions/2026/rollout-selected.jsonl").read_bytes() == before


@pytest.mark.parametrize("bad_id", ["", "../selected", "*", "selected/other"])
def test_invalid_session_identifiers_refuse(tmp_path, bad_id):
    home = _home(tmp_path)
    before = _snapshot(home)
    with pytest.raises(SystemExit, match="Session ID"):
        cli.main(
            [
                "codex-sessions",
                "repair",
                "--codex-home",
                str(home),
                "--session-id",
                bad_id,
                "--to",
                "codex-lb",
                "--yes",
                "--json",
            ]
        )
    assert _snapshot(home) == before


def test_json_repair_without_yes_never_prompts(tmp_path, monkeypatch):
    home = _home(tmp_path)
    before = _snapshot(home)
    monkeypatch.setattr("sys.stdin.isatty", lambda: True)
    monkeypatch.setattr("builtins.input", lambda _: pytest.fail("JSON output must not contain an interactive prompt"))
    with pytest.raises(SystemExit, match="JSON repair requires --yes"):
        _run(home, "repair", "--to", "codex-lb", "--json")
    assert _snapshot(home) == before


def test_duplicate_sqlite_ids_refuse_before_any_write(tmp_path):
    home = _home(tmp_path, jsonl_provider="codex-lb", db_provider="openai")
    with _db(home / "state_5.sqlite") as conn:
        conn.execute("ALTER TABLE threads RENAME TO old_threads")
        conn.execute("CREATE TABLE threads AS SELECT * FROM old_threads")
        conn.execute("INSERT INTO threads SELECT * FROM old_threads WHERE id='selected'")
    before = _snapshot(home)
    with pytest.raises(SystemExit, match="ambiguous"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert _snapshot(home) == before


def test_wal_provider_change_at_rewrite_is_refused(tmp_path, monkeypatch):
    from app import codex_sessions_repair as repair

    home = _home(tmp_path)
    session = home / "sessions/2026/rollout-selected.jsonl"
    before = session.read_bytes()
    original_progress = repair._progress
    with _db(home / "state_5.sqlite") as writer:
        writer.execute("PRAGMA journal_mode=WAL")

        def change_on_rewrite(callback, phase, completed, total=None):
            original_progress(callback, phase, completed, total)
            if phase == "rewrite" and completed == 0:
                writer.execute("UPDATE threads SET model_provider='other' WHERE id='selected'")
                writer.commit()

        monkeypatch.setattr(repair, "_progress", change_on_rewrite)
        with pytest.raises(SystemExit, match="Stale.*Backup retained"):
            _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert session.read_bytes() == before


def test_sqlite_bind_mount_copy_fallback_preserves_other_rows(tmp_path, monkeypatch, capsys):
    from app import codex_sessions_retag as retag

    home = _home(tmp_path, jsonl_provider="codex-lb", db_provider="openai")
    original = retag._update_sqlite_provider_in_place

    def mounted_write(path, *args, **kwargs):
        if path == home / "state_5.sqlite":
            raise sqlite3.OperationalError("unable to open database file")
        return original(path, *args, **kwargs)

    monkeypatch.setattr(retag, "_update_sqlite_provider_in_place", mounted_write)
    _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert json.loads(capsys.readouterr().out)["sqlite_rows_updated"] == 1
    with _db(home / "state_5.sqlite") as conn:
        assert conn.execute("SELECT id, model_provider FROM threads ORDER BY id").fetchall() == [
            ("other", "openai"),
            ("selected", "codex-lb"),
        ]


def test_global_preview_reports_consistent_incomplete_and_mismatch(tmp_path, capsys):
    home = _home(tmp_path)
    (home / "sessions/2026/unrelated.jsonl").unlink()
    new = home / "sessions/2026/consistent.jsonl"
    new.write_text('{"id":"consistent","model_provider":"openai"}\n', encoding="utf-8")
    with _db(home / "state_5.sqlite") as conn:
        conn.execute("INSERT INTO threads VALUES ('consistent','openai',?)", (str(new),))
    before = _snapshot(home)
    cli.main(["codex-sessions", "preview", "--codex-home", str(home), "--json", "--progress-json"])
    captured = capsys.readouterr()
    result = json.loads(captured.out)
    assert {session["session_id"]: session["status"] for session in result["sessions"]} == {
        "consistent": "consistent",
        "other": "incomplete",
        "selected": "mismatch",
    }
    assert [json.loads(line)["phase"] for line in captured.err.splitlines()] == ["discovery", "complete"]
    assert _snapshot(home) == before


def test_missing_sqlite_id_column_is_refused(tmp_path):
    home = _home(tmp_path)
    with _db(home / "state_5.sqlite") as conn:
        conn.execute("ALTER TABLE threads RENAME COLUMN id TO unrelated_id")
    before = _snapshot(home)
    with pytest.raises(SystemExit, match="id or thread_id"):
        _run(home, "repair", "--to", "codex-lb", "--yes", "--json")
    assert _snapshot(home) == before


def test_thread_id_alias_and_legacy_sqlite_column(tmp_path, capsys):
    home = _home(tmp_path, jsonl_provider="codex-lb", db_provider="openai")
    with _db(home / "state_5.sqlite") as conn:
        conn.execute("ALTER TABLE threads RENAME COLUMN id TO thread_id")
        conn.execute("ALTER TABLE threads DROP COLUMN rollout_path")
    cli.main(
        [
            "codex-sessions",
            "repair",
            "--codex-home",
            str(home),
            "--thread-id",
            "selected",
            "--to",
            "codex-lb",
            "--yes",
            "--json",
        ]
    )
    assert json.loads(capsys.readouterr().out)["sqlite_rows_updated"] == 1


def test_preview_read_error_creates_no_copy_or_backup(tmp_path, monkeypatch):
    from app import codex_sessions_repair as repair

    home = _home(tmp_path)
    before = _snapshot(home)

    def deny_database(*args, **kwargs):
        raise sqlite3.OperationalError("unable to open database file")

    monkeypatch.setattr(repair, "_connect_sqlite", deny_database)
    with pytest.raises(SystemExit, match="unable to open"):
        _run(home, "preview", "--json")
    assert _snapshot(home) == before
