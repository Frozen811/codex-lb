## Why

Exactly five unverified registry records cover credential freshness and account quota admission. Guardian currently shares the eight-day request freshness gate despite its twelve-hour idle contract, and a bare credit flag incorrectly bypasses an exhausted secondary quota.

## What Changes

- UP-PR-2429: restore the fixed twelve-hour guardian admission and persisted-row recheck, preserving leadership, batching, paused status and refresh settlement.
- UP-PR-2119: require positive balance or unlimited credits for the secondary-quota override, preserving primary and operator-disabled precedence.
- UP-PR-2120: verify first-request recovery after refresh-only failure, including concurrent operator deletion and forced callers.
- UP-PR-2132: verify rejected credential generations survive late health writes and safe HTTP replacement respects ownership and settlement.
- UP-PR-2326: verify retained reset evidence on freshness-skipped polls, restart, current eligibility and durable deduplication.
- Update exactly these five source rows with current local evidence. UP-ISSUE-2327 remains unselected and unchanged; its schema/distributed probe work requires its own change.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `usage-refresh-policy`: independent guardian keepalive, spendable quota credits and deletion-safe preflight recovery.

## Impact

Production edits are scoped to guardian, usage quota and, if confirmed by regression, AuthManager. Existing accounts repository, streaming recovery and warmup implementations are checked through focused public/runtime and real SQLite tests. No migration, setting, dependency, dashboard layout, publication or deployment is introduced. Stable specs/context, regression tests and issues-check evidence are updated together.
