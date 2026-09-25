# database-migrations Specification Delta

## Requirements

### Requirement: Production-scale migration duration check gate

Database migrations SHALL be validated against a duration check gate to prevent unbatched, table-locking statements that block production deployments.
A static and benchmark check (`scripts/check_migration_durations.py`) SHALL verify that:
1. Data-backfill migrations on high-volume tables (`request_logs`, `usage_history`) use bounded batching rather than monolithic unindexed updates.
2. Migrations do not execute long-running full table scans without indexes or batching.
3. The check exits with code 0 when all migration operations conform to safe execution duration budgets, and non-zero when unsafe long-running operations are detected.

#### Scenario: Clean migrations pass duration check
- **WHEN** `python scripts/check_migration_durations.py` is executed
- **THEN** all migration files are analyzed
- **AND** the check exits with code 0
