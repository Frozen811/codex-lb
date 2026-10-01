from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest

from scripts.build_dashboard import dashboard_complete, ensure_dashboard

pytestmark = pytest.mark.unit


def _frontend(root: Path) -> None:
    frontend = root / "frontend"
    frontend.mkdir()
    (frontend / "package.json").write_text(json.dumps({"packageManager": "bun@1.3.14"}))


def _assets(root: Path) -> None:
    static = root / "app/static"
    (static / "assets").mkdir(parents=True, exist_ok=True)
    (static / "index.html").write_text('<script src="/assets/app.js"></script><link href="/assets/app.css">')
    (static / "assets/app.js").write_text("console.log('audit')")
    (static / "assets/app.css").write_text("body{}")


def test_complete_sdist_does_not_require_bun(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _assets(tmp_path)
    lookup = Mock(side_effect=AssertionError("prebuilt assets must not invoke Bun"))
    monkeypatch.setattr("scripts.build_dashboard.shutil.which", lookup)
    ensure_dashboard(tmp_path)
    lookup.assert_not_called()


@pytest.mark.parametrize("kind", ["no-index", "missing-js", "empty-css", "path-escape"])
def test_incomplete_dashboard_cannot_be_packaged(tmp_path: Path, kind: str) -> None:
    _assets(tmp_path)
    static = tmp_path / "app/static"
    if kind == "no-index":
        (static / "index.html").unlink()
    elif kind == "missing-js":
        (static / "assets/app.js").unlink()
    elif kind == "empty-css":
        (static / "assets/app.css").write_text("")
    else:
        (static / "index.html").write_text(
            '<script src="/assets/../../escape.js"></script><link href="/assets/app.css">'
        )
    assert not dashboard_complete(tmp_path)


def test_missing_bun_explains_source_prerequisite(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _frontend(tmp_path)
    monkeypatch.setattr("scripts.build_dashboard.shutil.which", lambda _: None)
    with pytest.raises(RuntimeError, match=r"Install bun@1\.3\.14.*release wheel"):
        ensure_dashboard(tmp_path)


def test_wrong_bun_version_rejected_before_install(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _frontend(tmp_path)
    monkeypatch.setattr("scripts.build_dashboard.shutil.which", lambda _: "bun")
    monkeypatch.setattr("scripts.build_dashboard.subprocess.check_output", lambda *a, **k: "1.4.2\n")
    run = Mock()
    monkeypatch.setattr("scripts.build_dashboard.subprocess.run", run)
    with pytest.raises(RuntimeError, match=r"needs bun@1\.3\.14; found Bun 1\.4\.2"):
        ensure_dashboard(tmp_path)
    run.assert_not_called()


@pytest.mark.parametrize("failure", ["install", "build", "output"])
def test_failed_frontend_build_stops_package_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    _frontend(tmp_path)
    monkeypatch.setattr("scripts.build_dashboard.shutil.which", lambda _: "bun")
    monkeypatch.setattr("scripts.build_dashboard.subprocess.check_output", lambda *a, **k: "1.3.14\n")

    def run(args: list[str], **kwargs: object) -> None:
        if failure in args:
            raise subprocess.CalledProcessError(1, args)

    monkeypatch.setattr("scripts.build_dashboard.subprocess.run", run)
    with pytest.raises((RuntimeError, subprocess.CalledProcessError)):
        ensure_dashboard(tmp_path)


def test_clean_source_uses_pinned_bun_and_frozen_lock(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _frontend(tmp_path)
    monkeypatch.setattr("scripts.build_dashboard.shutil.which", lambda _: "bun")
    monkeypatch.setattr("scripts.build_dashboard.subprocess.check_output", lambda *a, **k: "1.3.14\n")
    calls: list[list[str]] = []

    def run(args: list[str], **kwargs: object) -> None:
        calls.append(args)
        assert kwargs["cwd"] == tmp_path / "frontend"
        if args == ["bun", "run", "build"]:
            _assets(tmp_path)

    monkeypatch.setattr("scripts.build_dashboard.subprocess.run", run)
    ensure_dashboard(tmp_path)
    assert calls == [["bun", "install", "--frozen-lockfile"], ["bun", "run", "build"]]
    assert dashboard_complete(tmp_path)
