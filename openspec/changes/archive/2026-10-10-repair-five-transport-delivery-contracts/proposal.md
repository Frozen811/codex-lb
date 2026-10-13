## Why

Five unverified registry records cover capacity feedback, native terminal cleanup, Windows transport attribution, frameless bridge drops, and paused delivery. Per-stream queue limits leave total live payload across queues and blocked producers unbounded.

## What Changes

- Complete exactly UP-PR-1084, UP-PR-2472, UP-PR-2457, UP-PR-2075, and UP-PR-1903 in local scope.
- Add a fixed 256 MiB shared live-payload budget for HTTP bridge queues, including blocked producers, while retaining the existing five-second delivery stall limit.
- Fail the affected downstream operation with retained-prefix delivery and one terminal on aggregate budget exhaustion; preserve shared-reader siblings and accounting cleanup.
- Independently verify existing selector provenance, native terminal/lease cleanup, Windows route parity, and post-output frameless health/replay rules through their product paths.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: bound aggregate live bridge payload, preserve ordered failure delivery and release memory on cancellation, detach, drain and garbage collection.

## Impact

Runtime edits are limited to `app/modules/proxy/_service/http_bridge/queues.py` and `upstream_events.py`. New regressions live in `tests/unit/test_transport_delivery_contracts.py` and, if needed, a focused bridge integration file. Update `openspec/specs/responses-api-compat/spec.md` and `context.md`, this change's artifacts, and exactly five source rows plus the summary in `issues-check.md`. No new setting, migration, UI, dependency or publication. Preserve the 251 pre-existing dirty files from the initial snapshot.
