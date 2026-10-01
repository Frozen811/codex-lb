"""Fail closed unless a fork release has successful, exact-source main CI."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from scripts.release_versions import parse_tag, write_github_outputs

REQUIRED_WORKFLOWS = ("ci.yml", "release-guards.yml", "simplicity-budgets.yml", "windows-startup.yml")


class GitHub:
    def __init__(self, repository: str, token: str) -> None:
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
            raise ValueError("invalid GitHub repository")
        if repository.lower() == "soju06/codex-lb":
            raise ValueError("the fork publisher cannot publish upstream")
        self.repository = repository
        self.token = token

    def get(self, path: str) -> Any:
        request = Request(
            f"https://api.github.com/repos/{self.repository}/{path}",
            headers={
                "Authorization": f"Bearer {self.token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except HTTPError as exc:
            raise ValueError(f"GitHub source verification failed (HTTP {exc.code})") from None

    def pages(self, path: str, key: str | None = None) -> list[Any]:
        result: list[Any] = []
        separator = "&" if "?" in path else "?"
        for page in range(1, 11):
            payload = self.get(f"{path}{separator}per_page=100&page={page}")
            items = payload[key] if key else payload
            result.extend(items)
            if len(items) < 100:
                return result
        raise ValueError("GitHub pagination limit reached; refusing incomplete evidence")


def resolve_tag(api: GitHub, tag: str) -> str:
    target = api.get(f"git/ref/tags/{quote(tag, safe='')}")["object"]
    for _ in range(8):
        if target["type"] == "commit":
            sha = target["sha"]
            if not re.fullmatch(r"[0-9a-f]{40}", sha):
                raise ValueError("invalid tag commit SHA")
            return sha
        if target["type"] != "tag":
            break
        target = api.get(f"git/tags/{target['sha']}")["object"]
    raise ValueError("release tag does not resolve to a commit")


def verify_source_checks(api: GitHub, sha: str) -> list[dict[str, Any]]:
    evidence = []
    for workflow in REQUIRED_WORKFLOWS:
        query = urlencode({"head_sha": sha, "branch": "main", "event": "push"})
        runs = api.pages(f"actions/workflows/{workflow}/runs?{query}", "workflow_runs")
        matching = [
            run
            for run in runs
            if run["head_sha"] == sha
            and run["head_branch"] == "main"
            and run["event"] == "push"
            and run["path"] == f".github/workflows/{workflow}"
        ]
        if not matching:
            raise ValueError(f"missing exact-source main-push evidence: {workflow}")
        run = max(matching, key=lambda item: item["id"])
        if run["status"] != "completed" or run["conclusion"] != "success":
            raise ValueError(f"source workflow is not successful: {workflow} ({run['status']}/{run['conclusion']})")
        if workflow == "ci.yml":
            jobs = api.pages(f"actions/runs/{run['id']}/attempts/{run['run_attempt']}/jobs", "jobs")
            aggregate = [job for job in jobs if job["name"] == "CI Required"]
            if len(aggregate) != 1 or aggregate[0]["status"] != "completed" or aggregate[0]["conclusion"] != "success":
                raise ValueError("CI Required aggregate is missing or unsuccessful")
        evidence.append({"workflow": workflow, "run_id": run["id"], "attempt": run["run_attempt"]})

    return evidence


def verify_source(api: GitHub, tag: str, expected_sha: str = "") -> dict[str, Any]:
    release = parse_tag(tag)
    sha = resolve_tag(api, tag)
    if expected_sha and sha != expected_sha:
        raise ValueError("release tag moved since initial verification")
    if api.get("branches/main")["commit"]["sha"] != sha:
        raise ValueError("release tag must identify the current main commit")

    evidence = verify_source_checks(api, sha)

    metadata = api.get(f"releases/tags/{quote(tag, safe='')}")
    if metadata["tag_name"] != tag or metadata["prerelease"] != release.is_prerelease:
        raise ValueError("GitHub release channel disagrees with the tag")
    if metadata["assets"]:
        raise ValueError("release already has assets; refusing to overwrite or mix builds")
    if not release.is_prerelease:
        for existing in api.pages("releases"):
            if existing["draft"] or existing["prerelease"]:
                continue
            try:
                candidate = parse_tag(existing["tag_name"])
            except ValueError:
                continue  # Historic hardened tags are not valid candidates for this publisher.
            if not candidate.is_prerelease and tuple(map(int, candidate.base.split("."))) > tuple(
                map(int, release.base.split("."))
            ):
                raise ValueError("a newer stable release exists; refusing alias regression")
    return {
        "repository": api.repository,
        "tag": tag,
        "sha": sha,
        "version": release.version,
        "pypi_version": release.pypi_version,
        "is_prerelease": release.is_prerelease,
        "image": f"ghcr.io/{api.repository.lower()}",
        "checks": evidence,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--expected-sha", default="")
    parser.add_argument("--provenance-out", type=Path)
    args = parser.parse_args()
    result = verify_source(GitHub(os.environ["GITHUB_REPOSITORY"], os.environ["GH_TOKEN"]), args.tag, args.expected_sha)
    write_github_outputs({key: result[key] for key in ("sha", "version", "pypi_version", "is_prerelease", "image")})
    if args.provenance_out:
        args.provenance_out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"verified {result['tag']} at {result['sha']}; all required source workflows passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
