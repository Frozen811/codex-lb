## Why

Five unverified registry records describe SQLite authentication/startup contention, lost scheduler leadership, interrupted session reclamation, and API keys surviving owner disable. The local writer gate currently passes its reentrancy marker into child tasks, while authentication and startup writes can bypass that gate.

## What Changes

- Serialize login/OAuth and fingerprint writes with local SQLite writers, with transaction cleanup inside the gate where the operation owns its session.
- Restrict writer-gate reentrancy to its owning task and verify lease recovery after cancelled database work.
- Preserve invalidation and late-cleanup ownership when reclamation is cancelled or driver interruption fails.
- Independently verify existing owner-before-key locking and the PostgreSQL API race tests.
- Close exactly UP-ISSUE-2447, UP-ISSUE-1949, UP-ISSUE-1682, UP-ISSUE-1981 and UP-PR-2460 in the verified local scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `database-backends`: task-owned local writer admission, authentication/startup serialization, cancellation-safe reclamation.

## Impact

Database session admission and cleanup, OAuth persistence, database-backed auth limiting, fingerprint verification and scheduler lease writes; focused unit/integration tests and existing API-key owner race tests. No new settings, schema revision, dashboard UI, or credential format. Existing unrelated dirty work and all external verification limits remain preserved.
