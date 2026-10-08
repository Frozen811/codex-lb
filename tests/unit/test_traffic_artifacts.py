from __future__ import annotations

import hashlib
import json
import os
import stat
from pathlib import Path

import pytest

from scripts.traffic_analysis import artifacts
from scripts.traffic_analysis.artifacts import (
    atomic_write_json,
    atomic_write_text,
    file_attestation,
    file_digest,
    read_json,
)


def test_digest_and_attestation_stream_the_same_file(tmp_path: Path) -> None:
    source = tmp_path / "evidence.jsonl"
    payload = b"a" * (1024 * 1024 + 17)
    source.write_bytes(payload)

    digest = file_digest(source)
    attestation = file_attestation("semantic_path_b", source)

    assert digest == {"bytes": len(payload), "sha256": hashlib.sha256(payload).hexdigest()}
    assert attestation == {
        "label": "semantic_path_b",
        "path": str(source),
        **digest,
        "available": True,
        "error": None,
    }


def test_attestation_fails_closed_without_exposing_exception(tmp_path: Path) -> None:
    missing = tmp_path / "missing.jsonl"

    result = file_attestation("path_c", missing)

    assert result["available"] is False
    assert result["error"] == "FileNotFoundError"
    assert result["sha256"] is None


def test_atomic_writes_replace_content_and_honor_mode(tmp_path: Path) -> None:
    output = tmp_path / "nested" / "state.json"
    atomic_write_json(output, {"old": True}, mode=0o600)
    atomic_write_json(output, {"new": True}, mode=0o600)

    assert read_json(output) == {"new": True}
    if os.name != "nt":
        assert stat.S_IMODE(output.stat().st_mode) == 0o600
    else:
        assert output.stat().st_mode & stat.S_IWUSR
    assert list(output.parent.glob(".*.tmp")) == []

    text_output = tmp_path / "report.md"
    atomic_write_text(text_output, "# PASS\n")
    assert text_output.read_text() == "# PASS\n"
    assert json.loads(json.dumps(read_json(output))) == {"new": True}


def test_directory_fsync_is_not_attempted_when_unsupported(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setattr(artifacts, "_DIRECTORY_FSYNC_SUPPORTED", False)

    def unexpected_open(*args, **kwargs):
        pytest.fail("An unsupported directory handle must not be opened")

    monkeypatch.setattr(artifacts.os, "open", unexpected_open)
    artifacts._fsync_directory(tmp_path)


@pytest.mark.parametrize("stage", ["open", "sync"])
def test_supported_directory_errors_still_propagate(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, stage: str
) -> None:
    monkeypatch.setattr(artifacts, "_DIRECTORY_FSYNC_SUPPORTED", True)
    closed: list[int] = []

    def open_directory(*args, **kwargs):
        if stage == "open":
            raise PermissionError("denied directory")
        return 123

    def sync_directory(descriptor: int) -> None:
        assert descriptor == 123
        raise OSError("directory sync failed")

    monkeypatch.setattr(artifacts.os, "open", open_directory)
    monkeypatch.setattr(artifacts.os, "fsync", sync_directory)
    monkeypatch.setattr(artifacts.os, "close", closed.append)
    with pytest.raises(OSError):
        artifacts._fsync_directory(tmp_path)
    assert closed == ([123] if stage == "sync" else [])
