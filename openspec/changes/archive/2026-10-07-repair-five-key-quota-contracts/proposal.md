## Why

Five unchecked registry tasks (UP-ISSUE-2492, UP-ISSUE-2556, UP-ISSUE-1080, UP-ISSUE-631, UP-PR-2463) need product-path verification. Credit override windows look like enforced budgets, API-key observation windows are inaccessible in the dashboard, and per-account quota restrictions disappear when a process restarts.

## What Changes

- Persist account quota limits and project them into account selection, including cache invalidation and quota bypass boundaries.
- Label credit override windows as display-only and exclude them from traffic enforcement while preserving the legacy usage response.
- Connect selectable 7/30/60/90-day windows to API-key usage totals and charts.
- Preserve failed keys for bulk reset retries and show their names and errors.
- Independently verify estimated usage-share limits on subscription routes and durable demand accounting.

## Capabilities

### Modified Capabilities

- `api-keys`: observation windows, bulk reset outcomes, display-only credit overrides.
- `account-routing`: durable account quota restrictions.

## Impact

Account persistence and selection, one nullable forward migration, API-key dashboard views, targeted public-route tests and OpenSpec. No new environment settings or dependencies. Commit directly to main is explicitly requested; publication is not requested.
