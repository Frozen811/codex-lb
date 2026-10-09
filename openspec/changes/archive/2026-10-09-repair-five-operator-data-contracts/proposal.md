## Why

Five unverified registry records concern local data planning and migration diagnostics. Retag currently scans entire transcripts repeatedly, and the Alembic runner has neither per-revision progress nor conditional rollback recovery guidance. Existing merge and facet contracts need independent product-path verification.

## What Changes

- UP-PR-2325: bound retag metadata planning, reuse grouped SQLite counts, preserve opaque transcript bytes, report progress and retained backups.
- UP-PR-2322: add guarded recovery guidance to unknown-revision failures without relaxing migration or stamp behavior.
- UP-PR-2307: log online revision starts, execution and failures with elapsed time, retaining Alembic ownership and stdout compatibility.
- UP-PR-2518: verify SCIM/overflow merge parents, current single-head ancestry and populated branch round trips.
- UP-PR-2522: verify facet indexes, account enumeration and earliest-row probes at the current API/repository path; fix only reproduced defects.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `runtime-portability`: bounded local provider metadata retag and progress.
- `database-migrations`: private per-revision progress and conditional metadata-stamp recovery guidance.

## Impact

CLI retag planning and its existing callers; online Alembic environment and migration errors; focused CLI, file-backed SQLite, migration graph and request-log API tests. No new settings, migrations, dependencies, dashboard pixels or release metadata. Preserve prior dirty work and all other registry rows. Local work only; provider, external databases, hosted CI and deployment remain separate evidence scopes.
