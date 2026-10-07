import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

CI_WORKFLOW = Path(__file__).parents[2] / ".github" / "workflows" / "ci.yml"


def test_extended_properties_are_replayable_and_independent_of_required_ci() -> None:
    path = CI_WORKFLOW.with_name("extended-properties.yml")
    workflow = yaml.safe_load(path.read_text(encoding="utf-8"))
    triggers = workflow.get("on", workflow.get(True))
    assert set(triggers) == {"schedule", "workflow_dispatch"}
    assert triggers["schedule"] == [{"cron": "23 2 * * *"}]
    assert "seed" in triggers["workflow_dispatch"]["inputs"]
    assert workflow["permissions"] == {"contents": "read"}
    job = workflow["jobs"]["properties"]
    assert "needs" not in job
    steps = {step["name"]: step for step in job["steps"]}
    run = steps["Run selected extended properties"]["run"]
    assert "--hypothesis-profile=thorough" in run
    assert '--hypothesis-seed "$HYPOTHESIS_SEED"' in run
    assert "-m extended_property" in run
    assert steps["Run selected extended properties"]["shell"] == "bash"
    assert "| tee .test-results/extended-properties/pytest.log" in run
    assert "--junitxml=" in run
    assert "continue-on-error" not in job
    assert "continue-on-error" not in steps["Run selected extended properties"]
    evidence = steps["Upload reproduction evidence"]
    assert evidence["if"] == "always()"
    assert evidence["with"]["include-hidden-files"] is True
    assert ".hypothesis/" in evidence["with"]["path"]
    assert "extended" not in _job_block(_ci_workflow_text(), "ci-required")


def _ci_workflow_text() -> str:
    return CI_WORKFLOW.read_text(encoding="utf-8")


def test_container_vulnerability_gate_precedes_report_publication_and_retains_evidence() -> None:
    docker = yaml.safe_load(_ci_workflow_text())["jobs"]["docker"]
    ordered_steps = docker["steps"]
    steps = {step["name"]: step for step in ordered_steps}
    names = list(steps)
    gate = steps["Enforce Trivy high-severity gate"]
    scan = steps["Scan Docker image with Trivy (SARIF)"]
    artifact = steps["Retain Trivy SARIF report"]
    upload = steps["Upload Trivy scan results to GitHub Security"]

    assert names.index("Enforce Trivy high-severity gate") < names.index("Scan Docker image with Trivy (SARIF)")
    assert names.index("Scan Docker image with Trivy (SARIF)") < names.index("Retain Trivy SARIF report")
    assert names.index("Retain Trivy SARIF report") < names.index("Upload Trivy scan results to GitHub Security")
    assert steps["Build Docker image"]["id"] == "docker-build"
    assert scan["id"] == "trivy-sarif"
    assert scan["if"] == "always() && steps.docker-build.outcome == 'success'"
    assert artifact["if"] == "always() && steps.trivy-sarif.outcome == 'success'"
    assert artifact["uses"].startswith("actions/upload-artifact@")
    assert artifact["with"]["path"] == scan["with"]["output"] == upload["with"]["sarif_file"]
    assert artifact["with"]["if-no-files-found"] == "error"
    assert "always() && steps.trivy-sarif.outcome == 'success'" in upload["if"]
    assert "github.event.pull_request.head.repo.full_name == github.repository" in upload["if"]
    assert gate["with"]["exit-code"] == 1
    assert gate["with"]["severity"] == "CRITICAL,HIGH"
    assert gate["with"]["ignore-unfixed"] is True
    assert gate["with"]["trivyignores"] == ".trivyignore"
    assert "continue-on-error" not in docker
    assert all("continue-on-error" not in step for step in (gate, scan, artifact, upload))


def _job_block(text: str, job_name: str) -> str:
    start_match = re.search(rf"^  {re.escape(job_name)}:\n", text, re.MULTILINE)
    assert start_match is not None
    next_job_match = re.search(r"^  [A-Za-z0-9_-]+:\n", text[start_match.end() :], re.MULTILINE)
    if next_job_match is None:
        return text[start_match.start() :]
    return text[start_match.start() : start_match.end() + next_job_match.start()]


def test_pytest_matrix_required_contexts_are_created_for_non_backend_prs() -> None:
    test_job = _job_block(_ci_workflow_text(), "test")

    assert "name: Tests (pytest, ${{ matrix.slice.name }})" in test_job
    assert "matrix:" in test_job
    assert "\n    if: needs.changes.outputs.backend == 'true'" not in test_job
    assert "name: Skip backend tests for unrelated changes" in test_job
    assert "if: needs.changes.outputs.backend != 'true'" in test_job
    assert "required pytest context satisfied" in test_job


def test_pytest_matrix_real_test_steps_still_run_only_for_backend_changes() -> None:
    test_job = _job_block(_ci_workflow_text(), "test")

    assert "if: needs.changes.outputs.backend == 'true'\n        run: make test-${{ matrix.slice.name }}" in test_job
    for step_name in (
        "Checkout repository",
        "Download built dashboard",
        "Set up uv",
    ):
        step = test_job.split(f"- name: {step_name}", maxsplit=1)[1]
        assert step.lstrip().startswith("if: needs.changes.outputs.backend == 'true'")


def test_postgres_required_context_is_created_for_non_backend_prs() -> None:
    pg_job = _job_block(_ci_workflow_text(), "test-postgres")

    assert "name: Tests (pytest, PostgreSQL)" in pg_job
    assert "\n    if: needs.changes.outputs.backend == 'true'" not in pg_job
    assert "name: Skip PostgreSQL tests for unrelated changes" in pg_job
    assert "if: needs.changes.outputs.backend != 'true'" in pg_job
    assert "required PostgreSQL context satisfied" in pg_job


def test_postgres_real_test_steps_still_run_only_for_backend_changes() -> None:
    pg_job = _job_block(_ci_workflow_text(), "test-postgres")

    assert "if: needs.changes.outputs.backend == 'true'\n        run: make test-postgres" in pg_job
    for step_name in (
        "Checkout repository",
        "Download built dashboard",
        "Set up uv",
    ):
        step = pg_job.split(f"- name: {step_name}", maxsplit=1)[1]
        assert step.lstrip().startswith("if: needs.changes.outputs.backend == 'true'")


def test_mysql_matrix_has_three_required_contexts_and_isolated_services() -> None:
    jobs = yaml.safe_load(_ci_workflow_text())["jobs"]
    mysql = jobs["test-mysql"]
    shards = mysql["strategy"]["matrix"]["shard"]
    assert shards == [1, 2, 3]
    assert mysql["strategy"]["fail-fast"] is False
    assert {mysql["name"].replace("${{ matrix.shard }}", str(shard)) for shard in shards} == {
        "Tests (pytest, MySQL, shard 1)",
        "Tests (pytest, MySQL, shard 2)",
        "Tests (pytest, MySQL, shard 3)",
    }
    assert mysql["services"]["mysql"]["image"] == "mysql:8.4"
    assert "test-mysql" in jobs["ci-required"]["needs"]
    assert "test-mysql-required" in jobs["ci-required"]["needs"]
    assert jobs["test-mysql-required"]["needs"] == ["test-mysql"]
    assert jobs["test-mysql-required"]["name"] == "Tests (pytest, MySQL)"


def test_mysql_shards_keep_placeholder_artifact_and_report_contracts() -> None:
    mysql = _job_block(_ci_workflow_text(), "test-mysql")
    assert "if: always() && !cancelled()" in mysql
    assert "name: Skip MySQL tests for unrelated changes" in mysql
    assert "if: needs.changes.outputs.backend != 'true'" in mysql
    assert "run: make test-mysql-${{ matrix.shard }}" in mysql
    assert "--junitxml=.test-results/mysql-${{ matrix.shard }}.xml" in mysql
    assert "name: mysql-durations-${{ matrix.shard }}" in mysql
    assert "path: .test-results/mysql-${{ matrix.shard }}.xml" in mysql
    assert "if: always() && needs.changes.outputs.backend == 'true'" in mysql
    for step_name in (
        "Checkout repository",
        "Download built dashboard",
        "Set up uv",
        "Run MySQL tests shard ${{ matrix.shard }}",
    ):
        step = mysql.split(f"- name: {step_name}", maxsplit=1)[1]
        assert step.lstrip().startswith("if: needs.changes.outputs.backend == 'true'")


@pytest.mark.parametrize("result", ["success", "failure", "skipped", "cancelled"])
def test_mysql_aggregate_requires_success_from_the_entire_matrix(result: str) -> None:
    jobs = yaml.safe_load(_ci_workflow_text())["jobs"]
    aggregate = jobs["test-mysql-required"]
    assert aggregate["if"] == "always()"
    run = aggregate["steps"][0]["run"]
    script = run.split("<<'PY'\n", maxsplit=1)[1].rsplit("\nPY", maxsplit=1)[0]
    env = os.environ.copy()
    env["NEEDS_JSON"] = json.dumps({"test-mysql": {"result": result}})
    process = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, text=True, timeout=30)
    assert process.returncode == (0 if result == "success" else 1), process.stderr


def test_dashboard_browser_smoke_covers_both_contract_sides_and_is_required() -> None:
    workflow = _ci_workflow_text()
    browser_job = _job_block(workflow, "dashboard-browser-smoke")
    required_job = _job_block(workflow, "ci-required")

    assert "needs.changes.outputs.backend == 'true' || needs.changes.outputs.frontend == 'true'" in browser_job
    assert "bun run playwright install --with-deps chromium" in browser_job
    assert "run: make test-dashboard-browser-smoke" in browser_job
    assert "- dashboard-browser-smoke" in required_job


def test_backend_consumers_share_one_dashboard_build_without_losing_placeholder_checks() -> None:
    workflow = _ci_workflow_text()
    build = _job_block(workflow, "frontend-build")
    assert "needs.changes.outputs.backend == 'true'" in build
    assert "name: Upload built dashboard" in build
    for name in ("test", "test-integration-core", "test-postgres", "test-mysql", "dashboard-browser-smoke", "package"):
        consumer = _job_block(workflow, name)
        assert "needs: [changes, frontend-build]" in consumer
        assert 'FRONTEND_BUILT: "1"' in consumer
        assert "name: Download built dashboard" in consumer
        assert "if: always() && !cancelled()" in consumer
    core = _job_block(workflow, "test-integration-core")
    assert "shard: [1, 2, 3, 4, 5, 6]" in core
    assert "fail-fast: false" in core
    assert "name: Upload integration durations" in core


def test_openspec_validation_is_required_for_spec_only_changes() -> None:
    workflow = _ci_workflow_text()
    trigger_block = workflow.split("concurrency:", maxsplit=1)[0]

    openspec_job = _job_block(workflow, "openspec")
    required_job = _job_block(workflow, "ci-required")

    assert "pull_request:" in trigger_block
    assert "paths:" not in trigger_block
    assert "paths-ignore:" not in trigger_block
    assert "\n    needs:" not in openspec_job
    assert "\n    if:" not in openspec_job
    assert "npx --yes @fission-ai/openspec@1.11.0 validate --specs" in openspec_job
    assert "fetch-depth: 0" in openspec_job
    assert "python3 .github/scripts/validate_changed_openspec.py" in openspec_job
    assert "- openspec" in required_job


def test_rust_job_runs_native_routed_wire_probe_with_built_helper() -> None:
    workflow = _ci_workflow_text()
    rust_job = _job_block(workflow, "rust")
    required_job = _job_block(workflow, "ci-required")

    build = "cargo build --locked -p codex-lb-egress-worker --bin codex-lb-native-egress"
    probe = "uv run pytest -q -ra tests/integration/test_native_routed_egress.py"
    assert build in rust_job
    assert probe in rust_job
    assert rust_job.index(build) < rust_job.index(probe)
    assert "uses: astral-sh/setup-uv@20cfd1bf945f4377ade1205e4dbc17946fc9a30d" in rust_job
    assert "uv sync --dev --frozen" in rust_job
    assert (
        "CODEX_LB_NATIVE_EGRESS_TEST_BINARY: ${{ github.workspace }}/target/debug/codex-lb-native-egress"
    ) in rust_job
    assert "- rust" in required_job


RELEASE_GUARDS_WORKFLOW = Path(__file__).parents[2] / ".github" / "workflows" / "release-guards.yml"


def _pull_request_trigger_types(text: str) -> set[str]:
    trigger_block = text.split("concurrency:", maxsplit=1)[0]
    pull_request_block = trigger_block.split("  pull_request:", maxsplit=1)[1]
    types_match = re.search(r"^    types: \[(?P<types>[^\]]*)\]$", pull_request_block, re.MULTILINE)
    assert types_match is not None
    return {item.strip() for item in types_match.group("types").split(",")}


def test_ci_matrix_does_not_restart_on_pr_metadata_edits() -> None:
    workflow = _ci_workflow_text()

    # ci.yml cancels the in-flight run per ref, so any extra trigger type
    # restarts ~30 jobs for an unchanged head. `edited` (title/body PATCH by
    # agents and review bots) must therefore never be a ci.yml trigger.
    assert "cancel-in-progress: true" in workflow
    assert _pull_request_trigger_types(workflow) == {"opened", "reopened", "synchronize", "ready_for_review"}

    # The PR-body-dependent release guards live in release-guards.yml, and the
    # aggregate must not reference a job that no longer exists here.
    assert re.search(r"^  beta-release-guard:\n", workflow, re.MULTILINE) is None
    assert re.search(r"^  stable-release-guard:\n", workflow, re.MULTILINE) is None
    assert "- beta-release-guard" not in _job_block(workflow, "ci-required")


def test_release_guards_revalidate_pr_metadata_edits_in_their_own_workflow() -> None:
    workflow = RELEASE_GUARDS_WORKFLOW.read_text(encoding="utf-8")

    assert _pull_request_trigger_types(workflow) == {"opened", "reopened", "synchronize", "edited", "ready_for_review"}
    assert "group: ${{ github.workflow }}-${{ github.ref }}" in workflow

    beta_job = _job_block(workflow, "beta-release-guard")
    stable_job = _job_block(workflow, "stable-release-guard")
    # Check context names are unchanged from their ci.yml days.
    assert "name: Beta release guard" in beta_job
    assert "python -m scripts.guard_beta_release" in beta_job
    assert "name: Stable release guard" in stable_job
    assert "python -m scripts.guard_stable_release" in stable_job
