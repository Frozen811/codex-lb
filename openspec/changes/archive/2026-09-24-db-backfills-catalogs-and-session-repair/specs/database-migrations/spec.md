# database-migrations Specification Delta

## Requirements

### Requirement: Non-blocking, resumable, and observable data-backfill migrations

Data-backfill migrations on high-volume tables (`request_logs`, `usage_history`) MUST be non-blocking, resumable, and observable.
1. The migration MUST filter target rows by checking that destination columns are unpopulated (e.g. `useragent_group IS NULL`) to support safe resumption without redundant work.
2. The migration MUST process updates in bounded batches using primary key pagination rather than monolithic table scans.
3. The migration MUST log batch progress so operators and automated watchdogs observe execution progress.

#### Scenario: Data-backfill executes in bounded resumable batches
- **GIVEN** a table with unbackfilled rows
- **WHEN** the backfill migration executes
- **THEN** rows are updated in bounded batches
- **AND** execution is idempotent and safely resumes if interrupted
- **AND** progress is logged per batch
