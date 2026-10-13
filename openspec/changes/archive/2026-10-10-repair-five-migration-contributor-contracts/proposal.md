## Why

The migration duration checker silently misses raw updates because it compares lowercase table names with uppercased SQL. Its benchmark measures a Python list rather than migrations or a database, and is absent from CI. Three September lineage rows and contributor instruction guidance also lack independent registry verification.

## What Changes

- Repair the static duration gate and cover its CLI failure behavior.
- Add a disposable PostgreSQL benchmark with a production-scale synthetic request log fixture, actual migration execution, per-revision timing, budget enforcement and CI summaries.
- Verify the existing immutable September merge from each published branch, including downgrade/re-upgrade and preserved rows; do not adopt the rejected history-restamping proposal.
- Consolidate contributor instructions around OpenSpec, bounded ownership, pre-import test isolation and affected transport coverage.
- Update exactly UP-ISSUE-2474, UP-PR-2461, UP-PR-2462, UP-ISSUE-1471 and UP-ISSUE-2309 with evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `database-migrations`: genuine duration budgets, synthetic benchmark evidence and immutable September lineage.
- `user-documentation`: contributor guidance preserves gates while making bounded completion and test isolation explicit.

## Impact

Planned edits: `scripts/check_migration_durations.py`, new `scripts/benchmark_migrations.py`, focused duration and September migration tests, a dedicated `.github/workflows/migration-duration.yml`, `Makefile`, `AGENTS.md`, `issues-check.md`, and the two owning spec/context pairs plus this change. Existing migrations, runtime backfill behavior, application configuration and unrelated dirty work are preserved.
