## Why

Full CI #76 exposed duplicate `quota_limit_percent` DDL on SQLite, PostgreSQL and MySQL when startup bootstraps an existing schema whose Alembic ledger was lost or rewound. The published quota migration must remain immutable, and stored quota restrictions must survive recovery.

## What Changes

- Reconcile the quota-only revision during the normal locked upgrade path when its compatible column already exists.
- Apply every pending ancestor before marking only that proven additive revision as applied; preserve target resolution and reject incompatible columns.
- Cover preserved quota values, relative targets, missing columns and incompatible schema, and rerun existing bootstrap regressions.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `database-migrations`: Existing compatible quota restriction storage must survive ledger recovery without duplicate DDL or skipped ancestors.

## Impact

`app/db/migrate.py`, `tests/integration/test_account_quota_limit_migration.py`, existing migration regression suites and the owning OpenSpec capability. No published migration files, revision graph, dependencies or settings change.
