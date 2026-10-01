## Why

INSTALL-06/07/08 need actual public wheel/sdist installation checks and correct fork uv/pip commands. Historical packages advertise version 1.25.1 while runtime is 1.25.0-beta.9, the public sdist contains nested agent worktrees, and source-only Git builds omit the ignored dashboard assets. Bare index commands select upstream rather than the fork.

## What Changes

- Verify historical public package contents/source and clean installs without modifying those artifacts.
- Require Python source builds to include a complete dashboard, build missing assets using the pinned frontend toolchain, or fail with actionable prerequisite guidance.
- Fix documented Python installation channels, artifact identity and update/data preservation instructions.
- Validate locally rebuilt packages and Git-like source installs, then commit and push the accumulated verified fixes to a fork branch as requested.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: Python wheel/sdist/Git installation and frontend build prerequisites.

## Impact

Python packaging build hook, pyproject packaging rules, installation docs, focused tests, audit tracker. No new runtime settings, schema change, public artifact replacement or production data operation.
