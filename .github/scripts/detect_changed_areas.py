#!/usr/bin/env python3
"""Detect CI areas changed by a pull request with retrying GitHub API reads."""

from __future__ import annotations

import json
import os
import sys
from fnmatch import fnmatch
from pathlib import Path
from typing import Any

try:
    from github_api import GitHubApiError, next_link, request_json
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from github_api import GitHubApiError, next_link, request_json

FILTERS = {
    "frontend": [
        "frontend/**",
        "Makefile",
        ".github/workflows/ci.yml",
    ],
    "backend": [
        ".github/scripts/**",
        "app/**",
        "tests/**",
        "config/**",
        "scripts/**",
        "pyproject.toml",
        "uv.lock",
        "Makefile",
        ".github/workflows/ci.yml",
        "docs/reference/settings.md",
        ".env.example",
        ".github/simplicity-budgets.toml",
    ],
    "rust": [
        "Cargo.toml",
        "Cargo.lock",
        "rust-toolchain.toml",
        "deny.toml",
        "crates/**",
        "app/core/clients/codex.py",
        "app/core/clients/http.py",
        "app/core/clients/native_egress.py",
        "app/core/clients/usage.py",
        "app/core/clients/stream_errors.py",
        "app/core/clients/proxy.py",
        "app/core/clients/proxy_websocket.py",
        "app/core/config/settings.py",
        "app/core/openai/**",
        "app/core/upstream_proxy/**",
        "app/core/utils/proxy_env.py",
        "pyproject.toml",
        "uv.lock",
        "tests/unit/test_native_egress.py",
        "tests/unit/test_usage_client.py",
        "tests/unit/test_native_egress_packaging.py",
        "tests/unit/test_native_sse_fixtures.py",
        "tests/integration/test_native_routed_egress.py",
        "tests/integration/test_native_sse_egress.py",
        "tests/integration/test_native_usage_egress.py",
        "Dockerfile",
        "Dockerfile.*",
        "Makefile",
        ".github/workflows/ci.yml",
    ],
    "helm": [
        "deploy/helm/**",
        "Makefile",
        ".github/workflows/ci.yml",
    ],
    "docker": [
        "Dockerfile",
        "Dockerfile.*",
        ".dockerignore",
        "docker-compose*.yml",
        "app/**",
        "config/**",
        "frontend/**",
        "scripts/**",
        "pyproject.toml",
        "uv.lock",
        ".github/workflows/ci.yml",
    ],
    "migrations": [
        "app/db/alembic/**",
        "pyproject.toml",
        "uv.lock",
        ".github/workflows/ci.yml",
    ],
    "nix": [
        "flake.nix",
        "flake.lock",
        "frontend/**",
        "app/**",
        "config/**",
        "scripts/hatch_build.py",
        "scripts/build_dashboard.py",
        "LICENSE",
        "README.md",
        "pyproject.toml",
        "uv.lock",
        ".github/workflows/ci.yml",
    ],
}

FULL_SUITE_PATTERNS = [
    ".github/workflows/**",
    ".github/scripts/detect_changed_areas.py",
    ".github/scripts/github_api.py",
    ".gitattributes",
]


def _full_suite_files(reason: str) -> list[str]:
    print(f"warning: {reason}; falling back to the full CI suite", flush=True)
    return [".github/workflows/ci.yml"]


def _event() -> dict[str, Any]:
    event_path = os.environ.get("GITHUB_EVENT_PATH")
    if not event_path:
        raise SystemExit("GITHUB_EVENT_PATH is required")
    return json.loads(Path(event_path).read_text(encoding="utf-8"))


def _pull_request_files(event: dict[str, Any]) -> list[str]:
    pull_request = event.get("pull_request")
    if not isinstance(pull_request, dict):
        raise SystemExit("pull_request event payload is required")
    files_url = pull_request.get("url")
    if not isinstance(files_url, str) or not files_url:
        raise SystemExit("pull_request.url missing from event payload")
    expected_count = pull_request.get("changed_files")
    if type(expected_count) is not int or not 0 <= expected_count <= 3000:
        return _full_suite_files("PR changed-file count is missing, invalid or exceeds the API limit")
    url: str | None = f"{files_url}/files?per_page=100"
    files: list[str] = []
    seen_urls: set[str] = set()
    filenames: set[str] = set()
    while url:
        if url in seen_urls or len(seen_urls) >= 30:
            return _full_suite_files("PR file pagination repeats or exceeds the API limit")
        seen_urls.add(url)
        try:
            payload, link = request_json(url)
        except GitHubApiError as exc:
            return _full_suite_files(f"GitHub PR files request failed after retries: {exc}")
        if not isinstance(payload, list):
            return _full_suite_files("GitHub PR files response is not a list")
        for item in payload:
            if not isinstance(item, dict):
                return _full_suite_files("GitHub PR file entry is not an object")
            filename = item.get("filename")
            if not isinstance(filename, str) or not filename or filename in filenames:
                return _full_suite_files("GitHub PR file entry has a missing or repeated filename")
            filenames.add(filename)
            files.append(filename)
            previous = item.get("previous_filename")
            if "previous_filename" in item or item.get("status") == "renamed":
                if not isinstance(previous, str) or not previous:
                    return _full_suite_files("GitHub renamed file has no valid previous filename")
                files.append(previous)
        url = next_link(link)
    if len(filenames) != expected_count:
        return _full_suite_files("GitHub PR file list does not match the changed-file count")
    return files


def _matches(path: str, patterns: list[str]) -> bool:
    return any(fnmatch(path, pattern) for pattern in (*FULL_SUITE_PATTERNS, *patterns))


def main() -> int:
    files = _pull_request_files(_event())
    outputs = {name: any(_matches(path, patterns) for path in files) for name, patterns in FILTERS.items()}
    output_path = os.environ.get("GITHUB_OUTPUT")
    lines = [f"{name}={'true' if matched else 'false'}" for name, matched in outputs.items()]
    if output_path:
        with Path(output_path).open("a", encoding="utf-8") as fh:
            for line in lines:
                print(line, file=fh)
    for line in lines:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
