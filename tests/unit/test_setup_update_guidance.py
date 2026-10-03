from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit
_ROOT = Path(__file__).resolve().parents[2]


def test_update_commands_select_explicit_fork_without_origin_assumption():
    text = (_ROOT / "COMMUNITY_RELEASE.md").read_text(encoding="utf-8").split('<a id="how-to-update"></a>', 1)[1]
    commands = re.findall(r"```(?:bash|powershell)\n(.*?)\n```", text, re.DOTALL)
    assert commands
    assert all("git pull origin" not in block for block in commands)
    source_commands = [block for block in commands if "git fetch" in block]
    assert len(source_commands) == 2
    for block in source_commands:
        assert "https://github.com/Frozen811/codex-lb.git" in block
        assert "git switch --detach FETCH_HEAD" in block
        assert "git status --porcelain" in block
    assert "$LASTEXITCODE" in source_commands[0]
    assert "exit 1" in source_commands[1]


def test_platform_matrix_distinguishes_runtime_and_declared_targets():
    text = (_ROOT / "docs/deployment/python.md").read_text(encoding="utf-8")
    matrix = text.split("## Platform and topology evidence", 1)[1]
    assert "unknown/unknown" in matrix and "attestation-manifest" in matrix
    assert "aarch64-linux/aarch64-darwin" in matrix and "unexecuted" in matrix
    assert "py3-none-any" in matrix
    assert "Windows" in matrix and "Linux/amd64" in matrix and "macOS" in matrix
    assert "2026-10-02" in matrix


def test_kubernetes_rollback_does_not_promise_general_release_downgrade():
    text = (_ROOT / "docs/deployment/kubernetes.md").read_text(encoding="utf-8")
    assert "Rollback is supported to the immediately previous release only" not in text
    assert "not a general release rollback guarantee" in text
    assert "matching pre-upgrade database/key snapshot" in text
