## Why

Five unverified registry records cover shutdown, persistence observation, bridge heartbeat isolation and bounded SQLite usage reads. Current code can report a false drained state before ownership callbacks run and lets optional maintenance stall ring renewal.

## What Changes

- Complete exactly UP-PR-2506, UP-PR-2255, UP-PR-2344, UP-PR-2133 and UP-PR-2484 in independently verified local scope.
- Preserve cooperative database-task stopping and track cancellation-resistant work when its stop caller is interrupted.
- Report pending, drained or unknown persistence ownership without observing a false zero during callback transfer.
- Run bridge maintenance and cap refresh independently of ring renewal, with one owned task per phase and background-pool ring sessions.
- Verify retryable WebSocket upgrade denial and bounded SQLite history including recent-floor and timestamp-tie boundaries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `graceful-shutdown`: persistence ownership observation and interrupted stop tracking.
- `bridge-ring-membership`: isolated maintenance owners and ring connection admission.
- `query-caching`: independently verified capped SQLite history, recent-floor and timestamp-tie contracts.

## Impact

Application lifecycle, scheduler stopping, internal health status, detached persistence bookkeeping, ring sessions and focused tests. No new settings, schema migrations, dependencies, dashboard UI or release changes. Prior dirty work and the other 333 registry records remain preserved; live provider, POSIX process, PostgreSQL/MySQL runtime and cloud/public/production checks remain separate evidence scopes.
