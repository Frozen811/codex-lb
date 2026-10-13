from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from app.codex_retag_metadata import read_metadata, record_provider
from app.codex_sessions_retag import (
    PROVIDER_RETAG_BACKUP_DIR,
    ProgressCallback,
    _connect_sqlite,
    _create_backup,
    _find_jsonl_session_files,
    _find_state_dbs,
    _progress,
    _retag_jsonl_file,
    _update_sqlite_provider,
)

_PROVIDERS = {"openai", "codex-lb"}


@dataclass(frozen=True)
class SessionTag:
    path: Path
    provider: str | None
    rollout_path: Path | None = None


@dataclass(frozen=True)
class SessionPreview:
    session_id: str
    jsonl: tuple[SessionTag, ...]
    sqlite: tuple[SessionTag, ...]

    @property
    def status(self) -> Literal["consistent", "mismatch", "unsupported", "incomplete", "ambiguous"]:
        if any(tag.provider not in _PROVIDERS for tag in (*self.jsonl, *self.sqlite)):
            return "unsupported"
        if len(self.jsonl) > 1 or len({tag.path for tag in self.sqlite}) != len(self.sqlite):
            return "ambiguous"
        if not self.jsonl or not self.sqlite:
            return "incomplete"
        return "mismatch" if len({tag.provider for tag in (*self.jsonl, *self.sqlite)}) > 1 else "consistent"


@dataclass(frozen=True)
class RepairResult:
    session_id: str
    target_provider: str
    jsonl_files_updated: int
    sqlite_rows_updated: int
    tags_skipped: int
    backup_path: Path | None


def _validate_session_id(session_id: str) -> None:
    if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,255}", session_id) is None:
        raise ValueError("Session ID must be a nonempty identifier without path or wildcard characters")


def _safe_path(path: Path, parent: Path) -> Path:
    resolved = path.resolve()
    if (
        any(ancestor.is_symlink() for ancestor in (path, *path.parents) if ancestor != parent)
        or not resolved.is_relative_to(parent)
        or resolved == parent
    ):
        raise ValueError(f"Unsafe session metadata path: {path}")
    return resolved


def _read_state_tags(home: Path, session_id: str | None) -> dict[str, list[SessionTag]]:
    tags: dict[str, list[SessionTag]] = defaultdict(list)
    for db in _find_state_dbs(home):
        _safe_path(db, home)
        conn = _connect_sqlite(db, read_only=True)
        try:
            columns = {row[1] for row in conn.execute("PRAGMA table_info(threads)")}
            if "model_provider" not in columns:
                continue
            id_column = "id" if "id" in columns else "thread_id" if "thread_id" in columns else None
            if id_column is None:
                raise ValueError(f"Cannot select session without an id or thread_id column: {db}")
            path_column = "rollout_path" if "rollout_path" in columns else "NULL"
            where = f" WHERE {id_column} = ?" if session_id is not None else ""
            parameters = (session_id,) if session_id is not None else ()
            rows = conn.execute(f"SELECT {id_column}, model_provider, {path_column} FROM threads{where}", parameters)
            for row_id, provider, rollout in rows:
                if not isinstance(row_id, str) or not row_id:
                    raise ValueError(f"Missing session ID in {db}")
                if provider is not None and not isinstance(provider, str):
                    raise ValueError(f"Invalid session provider in {db}")
                rollout_path = None
                if rollout:
                    if not isinstance(rollout, str):
                        raise ValueError(f"Invalid rollout path in {db}")
                    path = Path(rollout)
                    rollout_path = _safe_path(path if path.is_absolute() else home / path, home / "sessions")
                tags[row_id].append(SessionTag(db, provider, rollout_path))
        finally:
            conn.close()
    return tags


def _header_tag(path: Path) -> tuple[str, SessionTag]:
    metadata = read_metadata(path)
    if len(metadata.records) != 1:
        raise ValueError(f"Missing or ambiguous initial session header: {path}")
    record = metadata.records[0]
    identities = [record.get(key) for key in ("id", "session_id", "thread_id")]
    payload = record.get("payload")
    if isinstance(payload, dict):
        identities.extend(payload.get(key) for key in ("id", "session_id", "thread_id"))
    ids = {value for value in identities if isinstance(value, str) and value}
    if len(ids) != 1 or any(value is not None and (not isinstance(value, str) or not value) for value in identities):
        raise ValueError(f"Missing or ambiguous session ID in {path}")
    return ids.pop(), SessionTag(path, record_provider(record))


def preview_codex_sessions(*, codex_home: Path, session_id: str | None = None) -> tuple[SessionPreview, ...]:
    if session_id is not None:
        _validate_session_id(session_id)
    home = codex_home.expanduser().resolve()
    state_tags = _read_state_tags(home, session_id)
    indexed_paths = (
        {tag.rollout_path for tag in state_tags.get(session_id, ()) if tag.rollout_path is not None}
        if session_id is not None
        else set()
    )
    paths = tuple(sorted(indexed_paths)) if indexed_paths else _find_jsonl_session_files(home / "sessions", session_id)
    jsonl_tags: dict[str, list[SessionTag]] = defaultdict(list)
    for path in paths:
        _safe_path(path, home / "sessions")
        row_id, tag = _header_tag(path)
        if session_id is not None and row_id != session_id:
            raise ValueError(f"Indexed header ID does not match selected session: {path}")
        jsonl_tags[row_id].append(tag)
    ids = {session_id} if session_id is not None else set(state_tags) | set(jsonl_tags)
    return tuple(
        SessionPreview(row_id, tuple(jsonl_tags.get(row_id, ())), tuple(state_tags.get(row_id, ())))
        for row_id in sorted(ids)
    )


def _identity(path: Path) -> tuple[int, int, int, int]:
    stat = path.stat()
    return stat.st_dev, stat.st_ino, stat.st_size, stat.st_mtime_ns


def _check_plan(home: Path, plan: SessionPreview, identities: dict[Path, tuple[int, int, int, int]]) -> None:
    for path, identity in identities.items():
        _safe_path(path, home)
        if _identity(path) != identity:
            raise ValueError(f"Stale session metadata target: {path}")
    if preview_codex_sessions(codex_home=home, session_id=plan.session_id) != (plan,):
        raise ValueError("Stale session metadata provider values")


def repair_codex_session(
    *,
    codex_home: Path,
    session_id: str,
    target_provider: str,
    progress_callback: ProgressCallback | None = None,
) -> RepairResult:
    if target_provider not in _PROVIDERS:
        raise ValueError("Unsupported target provider; expected openai or codex-lb")
    home = codex_home.expanduser().resolve()
    _progress(progress_callback, "discovery", 0)
    plan = preview_codex_sessions(codex_home=home, session_id=session_id)[0]
    if plan.status not in {"mismatch", "consistent"}:
        raise ValueError(f"Cannot repair {session_id}: {plan.status} session metadata")
    jsonl = tuple(tag.path for tag in plan.jsonl if tag.provider != target_provider)
    databases = tuple(tag.path for tag in plan.sqlite if tag.provider != target_provider)
    skipped = sum(tag.provider == target_provider for tag in (*plan.jsonl, *plan.sqlite))
    if not jsonl and not databases:
        _progress(progress_callback, "complete", 0, 0)
        return RepairResult(session_id, target_provider, 0, 0, skipped, None)
    identities = {tag.path: _identity(tag.path) for tag in (*plan.jsonl, *plan.sqlite)}
    _safe_path(home / "backups" / PROVIDER_RETAG_BACKUP_DIR, home)
    _check_plan(home, plan, identities)
    backup = _create_backup(home, jsonl, databases, progress_callback)
    total = len(jsonl) + len(databases)
    jsonl_updated = 0
    rows_updated = 0
    source_provider = "openai" if target_provider == "codex-lb" else "codex-lb"
    try:
        _check_plan(home, plan, identities)
        _progress(progress_callback, "rewrite", 0, total)
        _check_plan(home, plan, identities)
        for path in jsonl:
            _safe_path(path, home / "sessions")
            if _identity(path) != identities[path]:
                raise ValueError(f"Stale session metadata target: {path}")
            if not _retag_jsonl_file(path, source_provider, target_provider, target_session_id=session_id):
                raise ValueError(f"Stale session metadata provider: {path}")
            jsonl_updated += 1
            _progress(progress_callback, "rewrite", jsonl_updated, total)
        for db in databases:
            _safe_path(db, home)
            if _identity(db) != identities[db]:
                raise ValueError(f"Stale session metadata target: {db}")
            current_tags = _read_state_tags(home, session_id).get(session_id, ())
            expected_tags = tuple(tag for tag in plan.sqlite if tag.path == db)
            if tuple(tag for tag in current_tags if tag.path == db) != expected_tags:
                raise ValueError(f"Stale session metadata provider values: {db}")
            updated = _update_sqlite_provider(db, source_provider, target_provider, target_session_id=session_id)
            if updated != 1:
                raise ValueError(f"Stale or ambiguous session row: {db}")
            rows_updated += updated
            _progress(progress_callback, "rewrite", jsonl_updated + rows_updated, total)
        _progress(progress_callback, "verification", 0, total)
        verified = preview_codex_sessions(codex_home=home, session_id=session_id)[0]
        expected = SessionPreview(
            session_id,
            tuple(SessionTag(tag.path, target_provider, tag.rollout_path) for tag in plan.jsonl),
            tuple(SessionTag(tag.path, target_provider, tag.rollout_path) for tag in plan.sqlite),
        )
        if verified != expected:
            raise ValueError("Session metadata repair verification failed")
        _progress(progress_callback, "verification", total, total)
        _progress(progress_callback, "complete", total, total)
    except Exception as exc:
        raise ValueError(f"{exc}. Backup retained at {backup}; changes may be partial.") from exc
    return RepairResult(session_id, target_provider, jsonl_updated, rows_updated, skipped, backup)
