## 1. Account operator repairs

- [x] 1.1 Repair portable backup metadata identity, explicit false/null settings and paused state; verify service and real backup HTTP round trips.
- [x] 1.2 Enforce operator quota caps before backoff and quota exemption; verify selection boundaries and persisted API cap changes.
- [x] 1.3 Verify paused credit cached visibility, selected-account observation, polling exclusion and redemption rejection with focused mapper/scheduler/API tests.
- [x] 1.4 Repair bulk remaining-credit ownership and generation fencing; verify real bulk HTTP partial-failure and multi-credit paths.
- [x] 1.5 Restore inclusive reset warm-up threshold and zero-default activation with retained legacy data; verify warm-up, settings, SQLite migration, dialect DDL and frontend validation tests.

## 2. Verification and closure

- [x] 2.1 Run focused regression suites, lint/type/architecture/topology and strict OpenSpec validation; record exact results and residuals.
- [x] 2.2 Synchronize capability specs/context, verify and archive the change; update and reread exactly five registry rows and prove all other source rows unchanged.
