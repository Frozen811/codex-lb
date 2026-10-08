## Why

Fork CI #80 at `f247f7ecbd99a2493fe60ca8b89523339277b7d0` stalled during Playwright's apt-get update for six hours, then the browser job was cancelled and CI Required failed. All 33 other CI jobs succeeded. Browser cache restoration does not eliminate the operating-system dependency installation, so that setup needs an explicit bound.

## What Changes

- Bound the dashboard browser-smoke job to twenty minutes and its Chromium/dependency installation step to ten minutes.
- Configure APT HTTP/HTTPS connection and data timeouts at thirty seconds with two acquisition retries on the ephemeral Ubuntu runner.
- Retain the existing `install --with-deps chromium`, browser tests, job conditions, and CI Required dependency.
- Add focused workflow regressions, record the cancelled run, and publish the fix to fork main with complete exact-head CI verification.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `github-automation`: browser-smoke dependency setup has bounded execution and still fails the required gate when installation cannot finish.

## Impact

Planned edits: `.github/workflows/ci.yml`, `tests/unit/test_ci_workflow_required_checks.py`, `openspec/specs/github-automation/spec.md` and `context.md`, `issues-check.md`, and this change's artifacts. No production code, CODEX_LB settings, lockfiles, release, deployment, or sixth source task.
