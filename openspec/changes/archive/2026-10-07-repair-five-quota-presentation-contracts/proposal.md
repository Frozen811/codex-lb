## Why

Five open records in issues-check.md need independent verification: UP-ISSUE-1918, UP-ISSUE-1367, UP-PR-2321, UP-PR-2489 and UP-PR-2468. Historical monthly quota mapping uses a broader duration threshold than ingestion and invents Team monthly credits, violating the observed-window contract.

## What Changes

- Align historical monthly presentation with the inclusive 28–32 day ingestion band and absent/zero-duration secondary placeholders.
- Preserve monthly percentages independently of capacity; leave unmeasured Team monthly capacity unknown and preserve newer short-window transitions.
- Verify Edu exhaustion on persisted usage/account API paths, account switching and sparse chart observations, and planner timezone rejection/legacy fallback.
- Record exact local evidence and update only the selected source rows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-quota-presentation`: consistent historical window classification and unknown monthly credit estimates.
- `account-routing`: retain Team monthly eligibility and freshness independently of estimated credits.

## Impact

Usage capacity defaults, account summaries and focused regression coverage. No new configuration, dependencies or migrations.
