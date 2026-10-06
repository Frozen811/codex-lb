import tempfile
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import smoke_release


class SharingViolation(PermissionError):
    winerror = 32


def test_smoke_directory_waits_for_windows_handles_then_removes_storage(monkeypatch):
    directory = tempfile.TemporaryDirectory(prefix="codex-lb-cleanup-test-")
    cleanup = directory.cleanup
    attempts = 0
    waits = []

    def release_handles():
        nonlocal attempts
        attempts += 1
        if attempts <= 2:
            raise SharingViolation("server.log is still closing")
        cleanup()

    monkeypatch.setattr(directory, "cleanup", release_handles)
    monkeypatch.setattr(smoke_release.tempfile, "TemporaryDirectory", lambda **kwargs: directory)
    monkeypatch.setattr(smoke_release, "time", SimpleNamespace(monotonic=lambda: 0.0, sleep=waits.append))
    with smoke_release.smoke_directory() as temporary:
        root = Path(temporary)
        (root / "server.log").write_text("readiness passed")
    assert not root.exists()
    assert attempts == 3
    assert waits == [0.05, 0.05]


def test_smoke_directory_does_not_ignore_persistent_windows_locks(monkeypatch):
    directory = tempfile.TemporaryDirectory(prefix="codex-lb-cleanup-test-")
    cleanup = directory.cleanup
    times = iter([0.0, 16.0])

    def locked():
        raise SharingViolation("server.log remains open")

    monkeypatch.setattr(directory, "cleanup", locked)
    monkeypatch.setattr(smoke_release.tempfile, "TemporaryDirectory", lambda **kwargs: directory)
    monkeypatch.setattr(
        smoke_release,
        "time",
        SimpleNamespace(monotonic=lambda: next(times), sleep=lambda _: pytest.fail("deadline already expired")),
    )
    try:
        with pytest.raises(SharingViolation, match="remains open"), smoke_release.smoke_directory():
            pass
    finally:
        cleanup()


def test_smoke_directory_does_not_ignore_unrelated_permission_errors(monkeypatch):
    directory = tempfile.TemporaryDirectory(prefix="codex-lb-cleanup-test-")
    cleanup = directory.cleanup

    def denied():
        raise PermissionError("permission denied")

    monkeypatch.setattr(directory, "cleanup", denied)
    monkeypatch.setattr(smoke_release.tempfile, "TemporaryDirectory", lambda **kwargs: directory)
    monkeypatch.setattr(
        smoke_release,
        "time",
        SimpleNamespace(monotonic=lambda: 0.0, sleep=lambda _: pytest.fail("not a sharing violation")),
    )
    try:
        with pytest.raises(PermissionError, match="permission denied"), smoke_release.smoke_directory():
            pass
    finally:
        cleanup()
