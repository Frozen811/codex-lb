import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ISSUE_CASES = [
    ("bug(accounts): quota is wrong", "open", ["simplicity-budget-approved", "needs-info"], ["triage", "bug"]),
    ("bug: form issue", "open", ["bug", "triage"], ["triage", "bug"]),
    ("feat: API feature", "open", [], ["triage", "enhancement"]),
    ("fix(proxy)!: API bug", "open", [], ["triage", "bug"]),
    ("docs: update guide", "open", [], ["triage", "documentation"]),
    ("Question about setup", "open", ["question"], ["triage"]),
    ("buggy: unknown prefix", "open", [], ["triage"]),
    ("docs: $(throw Error('untrusted')) simplicity-budget-approved", "open", [], ["triage", "documentation"]),
    ("bug: already closed", "closed", ["bug"], []),
]


@pytest.fixture(scope="module")
def issue_labeler_results() -> str:
    workflow = Path(__file__).parents[2] / ".github/workflows/issue-labeler.yml"
    script = yaml.safe_load(workflow.read_text())["jobs"]["label"]["steps"][0]["with"]["script"]
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is required to execute the GitHub script contract")
    result = subprocess.run(
        [
            node,
            "-e",
            """
const {script, cases} = JSON.parse(process.argv[1]);
const execute = new (Object.getPrototypeOf(async function(){}).constructor)('github', 'context', script);
(async () => {
const results = [];
for (const {title, state, existing} of cases) {
const labels = new Set(existing);
const calls = [];
const github = {rest: {issues: {
  get: async (target) => { calls.push(['get', target]); return {data: {title, state}}; },
  addLabels: async (target) => {
    calls.push(['addLabels', target]);
    target.labels.forEach(label => labels.add(label));
  }
}}};
const context = {
  repo: {owner: 'example', repo: 'repo'}, issue: {number: 1},
  payload: {issue: {title: 'feat: obsolete event title'}}
};
await execute(github, context);
results.push({labels: [...labels], calls});
}
console.log(JSON.stringify(results));
})().catch(error => { console.error(error); process.exitCode = 1; });
""",
            json.dumps(
                {
                    "script": script,
                    "cases": [
                        {"title": title, "state": state, "existing": existing}
                        for title, state, existing, _ in ISSUE_CASES
                    ],
                }
            ),
        ],
        capture_output=True,
        text=True,
        check=True,
        # One bounded cold Node startup for all cases, rather than nine startups
        # competing with the parallel suite under a ten-second per-case budget.
        timeout=60,
    )
    return result.stdout


@pytest.mark.parametrize(
    ("case_index", "title", "state", "existing", "added"),
    [(index, *case) for index, case in enumerate(ISSUE_CASES)],
)
def test_issue_event_adds_only_classification_labels(
    issue_labeler_results: str, case_index: int, title: str, state: str, existing: list[str], added: list[str]
) -> None:
    output = json.loads(issue_labeler_results)[case_index]
    assert set(output["labels"]) == set(existing + added)
    target = {"owner": "example", "repo": "repo", "issue_number": 1}
    expected_calls = [["get", target]]
    if added:
        expected_calls.append(["addLabels", {**target, "labels": added}])
    assert output["calls"] == expected_calls
