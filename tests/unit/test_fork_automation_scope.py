from pathlib import Path

import yaml

ROOT = Path(__file__).parents[2]
UPSTREAM = "github.repository == 'Soju06/codex-lb'"


def _workflow(name: str):
    return yaml.load((ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def test_upstream_release_cleanup_is_repository_scoped() -> None:
    release = _workflow("release.yml")
    assert UPSTREAM in release["jobs"]["release-metadata"]["if"]
    cleanup = release["jobs"]["withdraw-failed-release"]
    assert UPSTREAM in cleanup["if"]
    assert "always()" in cleanup["if"] and "github.event_name == 'release'" in cleanup["if"]
    assert "'failure'" in cleanup["if"] and "'cancelled'" in cleanup["if"]
    assert "--draft" in cleanup["steps"][0]["run"]


def test_upstream_automation_stays_confined_to_upstream() -> None:
    for workflow, job in (
        ("release-please.yml", "release-please"),
        ("prepare-beta-release.yml", "sync-beta-release-pr"),
        ("publish-beta-release.yml", "publish-beta-release"),
        ("update-upstream-metadata.yml", "refresh"),
    ):
        assert UPSTREAM in _workflow(workflow)["jobs"][job]["if"]


def test_fork_docs_resolve_pages_metadata_without_enabling_pages() -> None:
    workflow = _workflow("docs.yml")
    build = workflow["jobs"]["build"]
    assert build["permissions"] == {"contents": "read", "pages": "read"}
    pages = next(step for step in build["steps"] if step.get("id") == "pages")
    assert pages["uses"] == "actions/configure-pages@983d7736d9b0ae728b81ab479565c72886d7745b"
    assert pages["if"] == "github.event_name != 'pull_request' && github.ref == 'refs/heads/main'"
    assert pages["with"]["enablement"] == "false"
    render = next(step for step in build["steps"] if step.get("name") == "Build docs")
    assert render["env"]["PAGES_BASE_URL"] == "${{ steps.pages.outputs.base_url }}"
    assert "mkdocs build --strict" in render["run"]
    assert workflow["jobs"]["deploy"]["permissions"] == {"pages": "write", "id-token": "write"}


def test_fork_docs_metadata_targets_fork() -> None:
    config = yaml.load((ROOT / "mkdocs.yml").read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    assert config["repo_url"] == "https://github.com/Frozen811/codex-lb"
    assert config["repo_name"] == "Frozen811/codex-lb"
    assert config["site_url"] == ["PAGES_BASE_URL", "https://frozen811.github.io/codex-lb/"]
    assert config["edit_uri"] == "edit/main/docs/"


def test_docs_spec_links_target_fork() -> None:
    for page in (ROOT / "docs").rglob("*.md"):
        for kind in ("tree", "blob"):
            assert f"github.com/Soju06/codex-lb/{kind}/main/openspec/specs" not in page.read_text(encoding="utf-8"), (
                page
            )
