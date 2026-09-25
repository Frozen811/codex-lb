# Proposal: Account Backup/Restore, Quota Limit Restriction, and Database Migration Gates

## Summary
This change addresses Batch 38 (Tasks 139–142):
1. **Full Account Backup & Restore (Issue #850)**: Expose endpoints to export all configured accounts and configuration to a backup payload (`POST /api/accounts/backup/export`), and import a backup payload to restore accounts and settings (`POST /api/accounts/backup/restore`).
2. **Account Limit Restriction (Issue #631)**: Support setting a custom quota usage percentage cap per account (e.g., 50%) so that accounts can reserve cloud usage headroom and are excluded from selection once their usage exceeds the configured cap.
3. **Verified SQLite-to-PostgreSQL Migration Path Gate (Issue #2292)**: Provide verification tooling (`scripts/verify_sqlite_to_postgres_migration.py`) ensuring zero data loss and schema parity when migrating from SQLite to PostgreSQL.
4. **Long-Running Migrations Duration Gate (Issue #1471)**: Provide duration checking and static analysis tooling (`scripts/check_migration_durations.py`) to detect and gate unbatched table-locking statements on production-scale tables.
