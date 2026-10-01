from __future__ import annotations

import io
import subprocess
import tarfile
import zipfile
from pathlib import Path
from unittest.mock import Mock
from urllib.parse import urlparse

import pytest
import yaml

from scripts import guard_fork_release as gate
from scripts import smoke_release
from scripts.release_versions import parse_tag
from scripts.verify_release_artifacts import verify_archives
from tests.unit.test_release_versions import write_minimal_release_files

SHA = "a" * 40
OTHER_SHA = "b" * 40


class FakeGitHub(gate.GitHub):
    def __init__(self, tag: str = "v1.25.1") -> None:
        super().__init__("Frozen811/codex-lb", "unused")
        self.tag = tag
        self.tag_sha = self.main_sha = SHA
        self.annotated = False
        self.assets: list[dict] = []
        self.releases: list[dict] = []
        self.prerelease = parse_tag(tag).is_prerelease
        self.jobs = [{"name": "CI Required", "status": "completed", "conclusion": "success"}]
        self.runs: dict[str, list[dict[str, int | str | None]]] = {
            workflow: [
                {
                    "id": number,
                    "run_attempt": 2,
                    "path": f".github/workflows/{workflow}",
                    "head_sha": SHA,
                    "head_branch": "main",
                    "event": "push",
                    "status": "completed",
                    "conclusion": "success",
                }
            ]
            for number, workflow in enumerate(gate.REQUIRED_WORKFLOWS, 1)
        }

    def get(self, path: str):
        path = urlparse(path).path
        if path.startswith("git/ref/tags/"):
            return {"object": {"type": "tag" if self.annotated else "commit", "sha": self.tag_sha}}
        if path.startswith("git/tags/"):
            return {"object": {"type": "commit", "sha": self.tag_sha}}
        if path == "branches/main":
            return {"commit": {"sha": self.main_sha}}
        if path.startswith("actions/workflows/"):
            return {"workflow_runs": self.runs[path.split("/")[2]]}
        if path.startswith("actions/runs/"):
            assert "/attempts/2/jobs" in path
            return {"jobs": self.jobs}
        if path.startswith("releases/tags/"):
            return {"tag_name": self.tag, "prerelease": self.prerelease, "assets": self.assets}
        if path == "releases":
            return self.releases
        raise AssertionError(path)


@pytest.mark.parametrize("tag", ["v1.25.1", "v1.25.2-beta.1", "v1.25.2-alpha.1", "v1.25.2-rc.1"])
@pytest.mark.parametrize("annotated", [True, False])
def test_source_gate_accepts_valid_exact_source(tag: str, annotated: bool) -> None:
    api = FakeGitHub(tag)
    api.annotated = annotated
    result = gate.verify_source(api, tag, SHA)
    assert result["sha"] == SHA
    assert result["image"] == "ghcr.io/frozen811/codex-lb"
    assert len(result["checks"]) == 4
    assert result["pypi_version"] == parse_tag(tag).pypi_version


@pytest.mark.parametrize("workflow", gate.REQUIRED_WORKFLOWS)
@pytest.mark.parametrize(
    "status,conclusion",
    [
        ("completed", "failure"),
        ("completed", "cancelled"),
        ("completed", "skipped"),
        ("completed", "neutral"),
        ("completed", "timed_out"),
        ("queued", None),
        ("in_progress", None),
    ],
)
def test_source_gate_refuses_non_successful_latest_run(workflow: str, status: str, conclusion: str | None) -> None:
    api = FakeGitHub()
    api.runs[workflow].append({**api.runs[workflow][0], "id": 100, "status": status, "conclusion": conclusion})
    with pytest.raises(ValueError, match="not successful"):
        gate.verify_source(api, api.tag)


@pytest.mark.parametrize("workflow", gate.REQUIRED_WORKFLOWS)
@pytest.mark.parametrize(
    "field,value",
    [
        ("head_sha", OTHER_SHA),
        ("event", "pull_request"),
        ("head_branch", "feature"),
        ("path", ".github/workflows/other.yml"),
    ],
)
def test_source_gate_refuses_wrong_source_evidence(workflow: str, field: str, value: str) -> None:
    api = FakeGitHub()
    api.runs[workflow][0][field] = value
    with pytest.raises(ValueError, match="missing exact-source"):
        gate.verify_source(api, api.tag)


@pytest.mark.parametrize("workflow", gate.REQUIRED_WORKFLOWS)
def test_source_gate_refuses_missing_workflow_evidence(workflow: str) -> None:
    api = FakeGitHub()
    api.runs[workflow] = []
    with pytest.raises(ValueError, match="missing exact-source"):
        gate.verify_source(api, api.tag)


def test_windows_startup_workflow_checks_source_events_and_installed_readiness() -> None:
    workflow = yaml.load(
        (Path(__file__).parents[2] / ".github/workflows/windows-startup.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert set(workflow["on"]) == {"push", "pull_request", "merge_group", "workflow_dispatch"}
    assert workflow["on"]["push"]["branches"] == ["main"]
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["test-windows-startup"]
    assert job["runs-on"] == "windows-latest"
    assert job["defaults"]["run"]["shell"] == "pwsh"
    commands = "\n".join(step.get("run", "") for step in job["steps"])
    assert "test_memory_monitor.py" in commands and "test_check_proxy_architecture.py" in commands
    assert "uv build --wheel" in commands
    assert "uv pip install --no-cache --link-mode copy" in commands
    assert "scripts.smoke_release --python $candidatePython" in commands
    assert "RUNNER_TEMP" in commands


@pytest.mark.parametrize("failure", ["missing", "main-moved", "tag-moved", "aggregate", "channel", "assets", "older"])
def test_source_gate_refuses_incomplete_or_stale_candidate(failure: str) -> None:
    api = FakeGitHub()
    if failure == "missing":
        api.runs["ci.yml"] = []
    elif failure == "main-moved":
        api.main_sha = OTHER_SHA
    elif failure == "tag-moved":
        api.tag_sha = OTHER_SHA
    elif failure == "aggregate":
        api.jobs[0]["conclusion"] = "skipped"
    elif failure == "channel":
        api.prerelease = True
    elif failure == "assets":
        api.assets = [{"name": "old.whl"}]
    else:
        api.releases = [{"tag_name": "v1.26.0", "draft": False, "prerelease": False}]
    with pytest.raises(ValueError):
        gate.verify_source(api, api.tag, SHA)


def test_gate_cli_does_not_emit_success_outputs_on_failure(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    api = FakeGitHub()
    api.runs["ci.yml"][0]["conclusion"] = "failure"
    monkeypatch.setattr(gate, "GitHub", lambda *args: api)
    monkeypatch.setenv("GITHUB_REPOSITORY", api.repository)
    monkeypatch.setenv("GH_TOKEN", "unused")
    monkeypatch.setenv("GITHUB_OUTPUT", str(tmp_path / "outputs"))
    monkeypatch.setattr("sys.argv", ["gate", "--tag", api.tag, "--provenance-out", str(tmp_path / "provenance")])
    with pytest.raises(ValueError, match="ci.yml"):
        gate.main()
    assert not (tmp_path / "outputs").exists()
    assert not (tmp_path / "provenance").exists()


def make_archives(root: Path, version: str = "1.25.1", *, corruption: str = "") -> Path:
    write_minimal_release_files(root, version)
    assets = root / "app/static/assets"
    assets.mkdir(parents=True)
    (root / "app/static/index.html").write_text("<html></html>")
    (assets / "index.js").write_text("const ok = true;")
    (assets / "index.css").write_text("body {}")
    package_version = parse_tag("v" + version).pypi_version
    contents = {
        path.relative_to(root).as_posix(): path.read_bytes() for path in (root / "app").rglob("*") if path.is_file()
    }
    if corruption == "source":
        contents["app/__init__.py"] = b'__version__ = "1.25.0-beta.9"\n'
    if corruption == "assets":
        del contents["app/static/assets/index.css"]
    metadata = f"Name: codex-lb\nVersion: {'1.25.0' if corruption == 'metadata' else package_version}\n".encode()
    dist = root / "dist"
    dist.mkdir()
    with zipfile.ZipFile(dist / f"codex_lb-{package_version}-py3-none-any.whl", "w") as archive:
        for name, value in contents.items():
            archive.writestr(name, value)
        archive.writestr(f"codex_lb-{package_version}.dist-info/METADATA", metadata)
    with tarfile.open(dist / f"codex_lb-{package_version}.tar.gz", "w:gz") as archive:
        source_files = {
            name: (root / name).read_bytes()
            for name in ("pyproject.toml", "frontend/package.json", "deploy/helm/codex-lb/Chart.yaml", "uv.lock")
        }
        for name, value in {**contents, **source_files, "PKG-INFO": metadata}.items():
            member = tarfile.TarInfo(f"codex_lb-{package_version}/{name}")
            member.size = len(value)
            archive.addfile(member, io.BytesIO(value))
    return dist


@pytest.mark.parametrize("version", ["1.25.1", "1.25.2-beta.1"])
def test_artifact_gate_accepts_coherent_archives(tmp_path: Path, version: str) -> None:
    dist = make_archives(tmp_path, version)
    verify_archives(tmp_path, dist, "v" + version)


@pytest.mark.parametrize("corruption", ["source", "assets", "metadata"])
def test_artifact_gate_refuses_invalid_archives(tmp_path: Path, corruption: str) -> None:
    dist = make_archives(tmp_path, corruption=corruption)
    with pytest.raises(ValueError):
        verify_archives(tmp_path, dist, "v1.25.1")


def test_fork_workflow_publishers_require_gate_and_smoke() -> None:
    workflow = yaml.load(
        (Path(__file__).parents[2] / ".github/workflows/docker-publish.yml").read_text(), Loader=yaml.BaseLoader
    )
    assert workflow["on"]["workflow_dispatch"]["inputs"]["tag"]["required"] == "true"
    assert workflow["concurrency"] == {"group": "fork-release-publication", "cancel-in-progress": "false"}
    publisher = workflow["jobs"]["build-and-publish"]
    assert publisher["needs"] == "source-gate"
    steps = publisher["steps"]
    names = [step.get("name", "") for step in steps]
    recheck = names.index("Recheck source and CI immediately before publication")
    login = names.index("Log in to GHCR after all gates")
    upload = names.index("Upload validated packages and provenance without clobber")
    push = names.index("Push exact image tags before stable aliases")
    assert names.index("Smoke isolated image and check identity") < recheck < login < upload < push
    assert '--expected-sha "$SOURCE_SHA"' in steps[recheck]["run"]
    assert "--clobber" not in steps[upload]["run"]
    assert 'if [ "$IS_PRERELEASE" = false ]' in steps[push]["run"]
    build = next(step for step in steps if step.get("name") == "Build local candidate without publishing")
    assert build["with"]["push"] == "false" and build["with"]["load"] == "true"
    assert build["with"]["platforms"] == "linux/amd64"
    for job in workflow["jobs"].values():
        for step in job["steps"]:
            if "uses" in step:
                assert len(step["uses"].split("@")[1]) == 40
    cleanup = workflow["jobs"]["withdraw-failed-release"]
    assert cleanup["needs"] == ["source-gate", "build-and-publish"]
    assert "always()" in cleanup["if"] and "cancelled" in cleanup["if"]
    assert "--draft" in cleanup["steps"][0]["run"]


def test_gate_pagination_refuses_truncated_evidence(monkeypatch: pytest.MonkeyPatch) -> None:
    api = gate.GitHub("Frozen811/codex-lb", "unused")
    monkeypatch.setattr(api, "get", lambda _: [None] * 100)
    with pytest.raises(ValueError, match="pagination limit"):
        api.pages("releases")


def read_tar_members(path: Path) -> list[tuple[tarfile.TarInfo, bytes]]:
    members = []
    with tarfile.open(path) as archive:
        for member in archive.getmembers():
            stream = archive.extractfile(member)
            assert stream is not None
            members.append((member, stream.read()))
    return members


@pytest.mark.parametrize("extra", [".kilo/worktrees/other/app/main.py", ".agents/skills/private.txt", ".env.local"])
def test_sdist_refuses_workspace_and_environment_files(tmp_path: Path, extra: str) -> None:
    dist = make_archives(tmp_path)
    archive_path = dist / "codex_lb-1.25.1.tar.gz"
    members = read_tar_members(archive_path)
    with tarfile.open(archive_path, "w:gz") as archive:
        for member, content in members:
            archive.addfile(member, io.BytesIO(content))
        member = tarfile.TarInfo("codex_lb-1.25.1/" + extra)
        member.size = 3
        archive.addfile(member, io.BytesIO(b"bad"))
    with pytest.raises(ValueError, match="local worktree or environment"):
        verify_archives(tmp_path, dist, "v1.25.1")


def test_smoke_retries_startup_reset_and_fetches_dashboard(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = []

    class Response(io.BytesIO):
        status = 200

        def __init__(self, content: bytes, content_type: str = "text/html") -> None:
            super().__init__(content)
            self.headers = {"Content-Type": content_type}

    def request(url: str, **kwargs):
        calls.append(url)
        if len(calls) == 1:
            raise ConnectionResetError("server starting")
        if url.endswith("/health/ready"):
            return Response(b'{"status":"ready"}', "application/json")
        if url.endswith("/"):
            return Response(b'<script src="/assets/a.js"></script><link href="/assets/a.css">')
        return Response(b"asset", "application/javascript" if url.endswith(".js") else "text/css")

    monkeypatch.setattr(smoke_release, "urlopen", request)
    monkeypatch.setattr(smoke_release.time, "sleep", lambda _: None)
    smoke_release.smoke_http("http://localhost:1")
    assert calls == [
        "http://localhost:1" + suffix
        for suffix in ("/health/ready", "/health/ready", "/", "/assets/a.js", "/assets/a.css")
    ]


def test_smoke_stops_when_server_exits(monkeypatch: pytest.MonkeyPatch) -> None:
    process = Mock(spec=subprocess.Popen)
    process.returncode = 1
    process.poll.return_value = 1
    monkeypatch.setattr(smoke_release, "urlopen", lambda *args, **kwargs: pytest.fail("server already exited"))
    with pytest.raises(ValueError, match="exited before readiness"):
        smoke_release.smoke_http("http://localhost:1", process)


def test_sdist_refuses_managed_version_drift(tmp_path: Path) -> None:
    dist = make_archives(tmp_path)
    archive_path = dist / "codex_lb-1.25.1.tar.gz"
    members = read_tar_members(archive_path)
    with tarfile.open(archive_path, "w:gz") as archive:
        for member, content in members:
            if member.name.endswith("/frontend/package.json"):
                content = b'{"version": "1.25.0"}'
                member.size = len(content)
            archive.addfile(member, io.BytesIO(content))
    with pytest.raises(ValueError, match="sdist release-managed file"):
        verify_archives(tmp_path, dist, "v1.25.1")
