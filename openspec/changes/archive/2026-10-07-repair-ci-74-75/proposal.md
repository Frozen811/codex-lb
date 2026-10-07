## Why

Fork CI #74 passed 1,751 frontend tests but failed on an OAuth copy-feedback timer firing after DOM teardown. CI #75 failed while uploading an already generated Trivy SARIF report, preventing the high-severity gate from running and leaving no retained scan report.

## What Changes

- Own OAuth copy-feedback timers and pending clipboard completion for the lifetime of the mounted control.
- Run the mandatory Trivy HIGH/CRITICAL gate before remote report publication and retain SARIF as a workflow artifact.
- Keep GitHub Security publication mandatory when its existing event condition permits it; do not suppress scan or upload failures.
- Add lifecycle regressions and workflow-order checks, then publish a fix and verify complete CI on its exact SHA.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `clipboard-copy-fallback`: Copy feedback must release timers and ignore completion after unmount.
- `github-automation`: Container vulnerability enforcement must precede remote report publication and retain scan evidence.

## Impact

`frontend/src/features/accounts/components/oauth-dialog.tsx` and its tests, `.github/workflows/ci.yml`, `tests/unit/test_ci_workflow_required_checks.py`, and the two owning OpenSpec capabilities. No dependencies, settings, API or visual layout changes.
