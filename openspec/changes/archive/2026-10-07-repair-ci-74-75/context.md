# CI #74 and #75 repair evidence

Base: `664c8b98f949329707e5cb4c62ab9ab522f26bcb`. The initial worktree was clean.

- [CI #74](https://github.com/Frozen811/codex-lb/actions/runs/37627671759), SHA `ba4512387d71ba51cf1f6c27e0b5303364bcfa36`: 191 frontend files / 1,751 tests passed, then an uncaught `ReferenceError: window is not defined` originated in the OAuth-local copy reset timer. Five new lifecycle cases failed before the code fix.
- [CI #75](https://github.com/Frozen811/codex-lb/actions/runs/37642214458), base SHA: both images, container smoke and SARIF generation passed. GitHub Security upload failed and the following high-severity gate was skipped. The log ended at `Uploading results` with no error annotation. The API returned only 17 created jobs for that incomplete run; it is not complete CI evidence. Earlier main Code Scanning analyses are present.

The local fix owns copy timers and guards late clipboard completion without changing focus behavior or feedback duration. The workflow evaluates the strict vulnerability policy before publication, keeps reports as artifacts, and retains blocking upload semantics. For example, closing a device dialog immediately after copying cancels feedback; a remote upload failure cannot skip the prior vulnerability gate.

## Local verification

- `bun run test src/features/accounts/components/oauth-dialog.test.tsx src/components/copy-button.test.tsx src/utils/clipboard.test.ts --maxWorkers=2`: **29 passed**. A focused V8-instrumented run of the same files also passed all 29; global coverage thresholds were disabled only for that subset invocation. Repository coverage settings and full cloud thresholds remain unchanged.
- `bun run typecheck`: passed.
- `bun run eslint src/features/accounts/components/oauth-dialog.tsx src/features/accounts/components/oauth-dialog.test.tsx`: passed.
- `uv run --no-sync pytest -q tests/unit/test_ci_workflow_required_checks.py tests/unit/test_github_ci_scripts.py`: **65 passed**; the new workflow assertion failed before the workflow fix.
- Focused Ruff check and format check: passed.
- Both delta requirements are synced to main specs, with stable rationale in the owning context files. Strict OpenSpec validation and archive are completed before publication.

Local Bun is 1.4.2; the full workflow uses its pinned runtime. Local validation does not certify Docker, Linux, databases, or remote report publication. The user authorized committing the fixes and starting another complete CI run; cloud results are recorded separately against the pushed SHA.

## First full cloud run

[CI #76](https://github.com/Frozen811/codex-lb/actions/runs/37645052511),
SHA `8d5f9e99ce33687893200f8676838d04d924cf82`, created and completed all
35 jobs. Frontend coverage and Docker passed. The strict Trivy gate ran,
`trivy-sarif` artifact `11493088294` was retained, and GitHub Security recorded
the analysis for this SHA without errors. Windows Startup Regression also
passed. Migration replay tests exposed duplicate quota column DDL across all
three databases; the workflow and aggregates remained failed. Follow-up
implementation and exact local limitations are recorded in
[quota migration replay](../2026-10-07-preserve-quota-limit-migration-replay/context.md).
