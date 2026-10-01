from __future__ import annotations

import subprocess
import sys
from unittest.mock import Mock

import pytest

from scripts import source_startup

pytestmark = pytest.mark.unit


@pytest.mark.parametrize("flag", ["-h", "--help"])
def test_source_help_does_not_require_frontend(flag: str, monkeypatch: pytest.MonkeyPatch) -> None:
    prepare = Mock(side_effect=AssertionError("help must not compile frontend"))
    cli = Mock()
    monkeypatch.setattr(source_startup, "ensure_dashboard", prepare)
    monkeypatch.setattr("app.cli.main", cli)
    monkeypatch.setattr(sys, "argv", ["source_startup.py", flag])
    source_startup.main()
    prepare.assert_not_called()
    cli.assert_called_once_with()
    assert sys.argv == ["codex-lb", flag]


def test_source_startup_prepares_assets_and_preserves_arguments(monkeypatch: pytest.MonkeyPatch) -> None:
    prepare = Mock()
    cli = Mock()
    args = ["--port", "2547", "--log-file", "directory with spaces/server.log"]
    monkeypatch.setattr(source_startup, "ensure_dashboard", prepare)
    monkeypatch.setattr("app.cli.main", cli)
    monkeypatch.setattr(sys, "argv", ["source_startup.py", *args])
    source_startup.main()
    prepare.assert_called_once_with(source_startup.Path(source_startup.__file__).resolve().parents[1])
    cli.assert_called_once_with()
    assert sys.argv == ["codex-lb", *args]


@pytest.mark.parametrize(
    "failure",
    [
        RuntimeError("Install bun@1.3.14"),
        OSError("tool unavailable"),
        subprocess.CalledProcessError(1, ["bun", "build"]),
    ],
)
def test_frontend_failure_prevents_server_start(
    failure: Exception, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    cli = Mock()
    monkeypatch.setattr(source_startup, "ensure_dashboard", Mock(side_effect=failure))
    monkeypatch.setattr("app.cli.main", cli)
    monkeypatch.setattr(sys, "argv", ["source_startup.py"])
    with pytest.raises(SystemExit) as exc:
        source_startup.main()
    assert exc.value.code == 1
    assert "Source startup failed:" in capsys.readouterr().err
    cli.assert_not_called()


def test_cli_failure_status_is_preserved(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(source_startup, "ensure_dashboard", Mock())
    monkeypatch.setattr("app.cli.main", Mock(side_effect=SystemExit(2)))
    monkeypatch.setattr(sys, "argv", ["source_startup.py", "--unknown-option"])
    with pytest.raises(SystemExit) as exc:
        source_startup.main()
    assert exc.value.code == 2
