from __future__ import annotations

import importlib.util
import io
import json
import urllib.error
from email.message import Message
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest


def _load_script_module(name: str) -> ModuleType:
    path = Path(".github/scripts") / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class _Response:
    headers = {"Link": '<https://api.github.test/next>; rel="next"'}

    def __enter__(self) -> "_Response":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return b'[{"login":"octocat"}]'


def test_github_api_request_json_sleeps_and_retries_transient_html(monkeypatch) -> None:
    github_api = _load_script_module("github_api")
    calls: list[str] = []
    sleeps: list[float] = []

    def fake_urlopen(request: Any, timeout: float) -> _Response:
        del timeout
        calls.append(request.full_url)
        if len(calls) == 1:
            raise urllib.error.HTTPError(
                request.full_url,
                503,
                "Service Unavailable",
                Message(),
                io.BytesIO(b"<html><title>Unicorn!</title></html>"),
            )
        return _Response()

    monkeypatch.setattr(github_api.urllib.request, "urlopen", fake_urlopen)

    payload, link = github_api.request_json(
        "https://api.github.test/repos/example/project/contributors",
        token=None,
        attempts=2,
        sleep=sleeps.append,
    )

    assert calls == [
        "https://api.github.test/repos/example/project/contributors",
        "https://api.github.test/repos/example/project/contributors",
    ]
    assert sleeps == [2.0]
    assert payload == [{"login": "octocat"}]
    assert link == '<https://api.github.test/next>; rel="next"'


def test_detect_changed_areas_falls_back_to_full_suite_after_github_outage(monkeypatch) -> None:
    detect_changed_areas = _load_script_module("detect_changed_areas")

    def fail_request_json(url: str):
        del url
        raise detect_changed_areas.GitHubApiError("HTTP 503: <html>Unicorn!</html>")

    monkeypatch.setattr(detect_changed_areas, "request_json", fail_request_json)

    files = detect_changed_areas._pull_request_files(
        {"pull_request": {"url": "https://api.github.test/prs/1", "changed_files": 1}}
    )

    assert all(
        any(detect_changed_areas._matches(path, patterns) for path in files)
        for patterns in detect_changed_areas.FILTERS.values()
    )


@pytest.mark.parametrize(
    "path",
    [
        "app/core/clients/codex.py",
        "app/core/clients/http.py",
        "app/core/clients/proxy.py",
        "app/core/clients/proxy_websocket.py",
        "app/core/config/settings.py",
        "app/core/openai/requests.py",
        "app/core/upstream_proxy/router.py",
        "app/core/utils/proxy_env.py",
        "pyproject.toml",
        "uv.lock",
    ],
)
def test_native_routed_python_paths_trigger_rust_probe(path: str) -> None:
    detect_changed_areas = _load_script_module("detect_changed_areas")

    assert detect_changed_areas._matches(path, detect_changed_areas.FILTERS["rust"])


def _detect_outputs(monkeypatch, tmp_path: Path, pages, *, changed_files=1) -> dict[str, bool]:
    detector = _load_script_module("detect_changed_areas")
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"pull_request": {"url": "https://api.github.test/prs/1", "changed_files": changed_files}}),
        encoding="utf-8",
    )
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))
    responses = iter(pages)
    monkeypatch.setattr(detector, "request_json", lambda url: next(responses))
    assert detector.main() == 0
    return {name: value == "true" for name, value in (line.split("=") for line in output.read_text().splitlines())}


def test_detector_cli_selects_both_sides_of_rename(monkeypatch, tmp_path: Path) -> None:
    outputs = _detect_outputs(
        monkeypatch,
        tmp_path,
        [([{"filename": "docs/example.py", "previous_filename": "app/example.py", "status": "renamed"}], None)],
    )
    assert outputs["backend"] and outputs["docker"] and outputs["nix"]


@pytest.mark.parametrize(
    ("payload", "count"),
    [
        ([{"filename": "docs/only.md"}], 2),
        ([{"filename": "docs/only.md"}], None),
        ([{"filename": "docs/only.md"}], True),
        ([{"filename": "docs/only.md"}], -1),
        ([{"filename": "docs/only.md"}], "1"),
        ([{"filename": "docs/only.md"}], 3001),
        ([{"filename": "docs/only.md"}], 0),
        ([{"filename": "docs/only.md"}, {"filename": "docs/only.md"}], 2),
        ([{"filename": "docs/only.md"}, {}], 2),
        ([{"filename": "docs/only.md", "status": "renamed"}], 1),
        ([{"filename": "docs/only.md", "previous_filename": 1}], 1),
        ([{"filename": ""}], 1),
        ([None], 1),
        ({"message": "not a file list"}, 1),
    ],
)
def test_detector_cli_uses_full_suite_for_incomplete_evidence(monkeypatch, tmp_path: Path, payload, count) -> None:
    assert all(_detect_outputs(monkeypatch, tmp_path, [(payload, None)], changed_files=count).values())


def test_detector_cli_reads_every_page(monkeypatch, tmp_path: Path) -> None:
    outputs = _detect_outputs(
        monkeypatch,
        tmp_path,
        [
            ([{"filename": "docs/only.md"}], '<https://api.github.test/next>; rel="next"'),
            ([{"filename": "app/main.py"}], None),
        ],
        changed_files=2,
    )
    assert outputs["backend"] and outputs["nix"]


def test_detector_cli_refuses_pagination_cycle(monkeypatch, tmp_path: Path) -> None:
    link = '<https://api.github.test/prs/1/files?per_page=100>; rel="next"'
    assert all(_detect_outputs(monkeypatch, tmp_path, [([{"filename": "docs/only.md"}], link)]).values())


@pytest.mark.parametrize(
    "path",
    [
        ".github/scripts/detect_changed_areas.py",
        ".github/scripts/github_api.py",
        ".github/workflows/docker-publish.yml",
        ".github/workflows/windows-startup.yml",
        ".gitattributes",
    ],
)
def test_detector_cli_selects_all_areas_for_ci_contract_changes(monkeypatch, tmp_path: Path, path: str) -> None:
    assert all(_detect_outputs(monkeypatch, tmp_path, [([{"filename": path}], None)]).values())


@pytest.mark.parametrize(
    "path",
    [
        "scripts/hatch_build.py",
        "scripts/build_dashboard.py",
        "app/main.py",
        "config/models.json",
        "frontend/src/App.tsx",
        "frontend/package.json",
        "frontend/index.html",
        "frontend/vite.config.ts",
        "LICENSE",
        "README.md",
    ],
)
def test_detector_cli_selects_nix_for_package_source_changes(monkeypatch, tmp_path: Path, path: str) -> None:
    outputs = _detect_outputs(monkeypatch, tmp_path, [([{"filename": path}], None)])
    assert outputs["nix"]
    if path.startswith("scripts/"):
        assert outputs["backend"] and outputs["docker"]


def test_detector_cli_preserves_selective_docs_checks(monkeypatch, tmp_path: Path) -> None:
    assert not any(_detect_outputs(monkeypatch, tmp_path, [([{"filename": "docs/client-setup.md"}], None)]).values())


def test_detector_cli_handles_no_changed_files(monkeypatch, tmp_path: Path) -> None:
    assert not any(_detect_outputs(monkeypatch, tmp_path, [([], None)], changed_files=0).values())


def test_detector_cli_discards_partial_list_after_later_api_failure(monkeypatch, tmp_path: Path) -> None:
    detector = _load_script_module("detect_changed_areas")
    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"pull_request": {"url": "https://api.github.test/prs/1", "changed_files": 2}}), encoding="utf-8"
    )
    output = tmp_path / "output"
    monkeypatch.setenv("GITHUB_EVENT_PATH", str(event))
    monkeypatch.setenv("GITHUB_OUTPUT", str(output))

    def request(url: str):
        if url.endswith("per_page=100"):
            return [{"filename": "docs/only.md"}], '<https://api.github.test/next>; rel="next"'
        raise detector.GitHubApiError("HTTP 503")

    monkeypatch.setattr(detector, "request_json", request)
    assert detector.main() == 0
    assert all(line.endswith("=true") for line in output.read_text().splitlines())
