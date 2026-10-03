from __future__ import annotations

import re
import tomllib
from pathlib import Path
from urllib.parse import urlsplit

import pytest

pytestmark = pytest.mark.unit
_ROOT = Path(__file__).resolve().parents[2]
_ENTRY_POINTS = ("README.md", "README.zh-CN.md")


@pytest.mark.parametrize("entry_point", _ENTRY_POINTS)
def test_fork_readme_operational_links_resolve_to_tracked_fork_guides(entry_point: str):
    text = (_ROOT / entry_point).read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    operational_links = [
        link for link in links if any(area in link for area in ("deployment/", "client-setup", "getting-started"))
    ]
    assert operational_links
    for link in operational_links:
        parsed = urlsplit(link)
        assert not parsed.scheme, f"Operational link must select a tracked fork guide: {link}"
        assert (_ROOT / parsed.path).is_file(), link
    assert "https://soju06.github.io/codex-lb/" in links  # Explicit comparative upstream overview remains attributed.
    assert all("soju06.github.io/codex-lb/" not in link or link.endswith("/codex-lb/") for link in links)


@pytest.mark.parametrize("entry_point", _ENTRY_POINTS)
def test_readme_bash_examples_do_not_include_powershell_launcher(entry_point: str):
    text = (_ROOT / entry_point).read_text(encoding="utf-8")
    text = re.sub(r"^> ?", "", text, flags=re.MULTILINE)
    examples = re.findall(r"```bash\n(.*?)\n```", text, re.DOTALL)
    assert examples
    assert all("run.ps1" not in example for example in examples)
    assert "docs/deployment/python.md#run-from-a-fork-checkout" in text
    assert "docs/deployment/docker.md#basic-run" in text


def test_source_selection_examples_use_named_shell_variables_and_fail_closed():
    text = (_ROOT / "docs/deployment/python.md").read_text(encoding="utf-8")
    examples = re.findall(r"```(bash|powershell)\n(.*?)\n```", text, re.DOTALL)
    selections = [(shell, block) for shell, block in examples if "git checkout" in block or "git+https://" in block]
    assert {shell for shell, _ in selections} == {"bash", "powershell"}
    assert len(selections) == 4
    for shell, block in selections:
        assert not re.search(r"(?<![\"'])<[\w-]+>", block)
        assert "REPLACE_WITH_REVIEWED_FULL_SHA" in block
        assert "{40}" in block
        if shell == "bash":
            assert '"$source_revision"' in block or '@$source_revision"' in block
            assert "exit 1" in block
        else:
            assert "$sourceRevision" in block
            assert "throw" in block


def test_release_client_configuration_uses_responses_wire_contract():
    text = (_ROOT / "COMMUNITY_RELEASE.md").read_text(encoding="utf-8")
    examples = re.findall(r"```toml\n(.*?)\n```", text, re.DOTALL)
    assert examples
    for example in examples:
        config = tomllib.loads(example)
        for provider in config.get("model_providers", {}).values():
            assert provider["wire_api"] == "responses"
            assert "wire_specification" not in provider


def test_kubernetes_chart_guidance_points_at_fork_chart():
    text = (_ROOT / "docs/deployment/kubernetes.md").read_text(encoding="utf-8")
    chart_links = re.findall(r"https://github.com/[^)\s]+/deploy/helm/codex-lb(?:/README.md)?", text)
    assert chart_links
    assert all(link.startswith("https://github.com/Frozen811/codex-lb/") for link in chart_links)


@pytest.mark.parametrize(
    "relative_path",
    ("docs/deployment/python.md", "docs/sso.md", "docs/traffic-parity.md", "deploy/helm/codex-lb/README.md"),
)
def test_shell_command_arguments_do_not_use_redirection_placeholders(relative_path: str):
    text = (_ROOT / relative_path).read_text(encoding="utf-8")
    examples = [
        body for _, body in re.findall(r"(?m)^( {0,3})```(?:bash|powershell)\n(.*?)^\1```[ \t]*$", text, re.DOTALL)
    ]
    assert examples
    for example in examples:
        commands = "\n".join(line for line in example.splitlines() if not line.lstrip().startswith("#"))
        assert not re.search(r"(?<![\"'])<(?:[\w-]+|your values[^>]*)>", commands), commands


def test_helm_recovery_commands_select_current_workload_kind():
    text = (_ROOT / "docs/sso.md").read_text(encoding="utf-8")
    commands = re.findall(r"^kubectl exec .+$", text, re.MULTILINE)
    assert commands
    assert all("statefulset/YOUR_WORKLOAD_NAME -c codex-lb" in command for command in commands)


@pytest.mark.parametrize("relative_path", ("docs/deployment/remote.md", "docs/telemetry.md"))
def test_bash_configuration_assignments_reach_child_service(relative_path: str):
    text = (_ROOT / relative_path).read_text(encoding="utf-8")
    examples = re.findall(r"```bash\n(.*?)\n```", text, re.DOTALL)
    assignments = [line for example in examples for line in example.splitlines() if re.search(r"CODEX_LB_\w+=", line)]
    assert assignments
    assert all(line.startswith("export ") for line in assignments)
