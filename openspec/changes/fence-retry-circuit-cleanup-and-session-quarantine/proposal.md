# Proposal: Fence Retry Circuit Cleanup and Isolate Session Quarantine

## Why
Two subtle concurrency races in the HTTP bridge state management allow active protection to be inadvertently cleared:
1. **Issue #2270**: Scheduled cleanup in `DurableBridgeRepository.purge_retry_circuits_before` selects stale retry-circuit candidates by key, but executes deletion without verifying that the row's `admission_generation` and `updated_at_epoch` have not advanced. If a replay claims a newer admission generation or a new failure updates the row between the `select` and `delete`, the scheduled cleanup deletes the active row, allowing unauthorized replays.
2. **Issue #2268**: In `_clear_http_bridge_quarantine`, an old HTTP bridge request completing late can clear a replacement session's quarantine. When a quarantined entry for key K is pruned/cleared and a new session B subsequently reuses key K and is quarantined, a new `_HTTPBridgeQuarantineEntry` is initialized with `generation = 0` and bumped to `1`. A delayed cleanup from previous session A presenting generation 1 clears session B's quarantine because generations were not monotonic per key across entry removals and entry ownership was not verified against session identity.

## What Changes
- In `app/modules/proxy/durable_bridge_repository.py` (`purge_retry_circuits_before`):
  - Include `updated_at_epoch` and `admission_generation` in the candidate selection query.
  - Add equality filters for `updated_at_epoch` and `admission_generation` to the `delete` statement so that any row modified after selection is spared from deletion.
- In `app/modules/proxy/_service/http_bridge/quarantine.py`:
  - Track a monotonic quarantine generation map per key on the service instance (`_http_bridge_quarantine_generations`) so that generations never reset to 0 when entries are pruned or removed.
  - Store the owning session's identity (`session_id`) in `_HTTPBridgeQuarantineEntry`.
  - In `_clear_http_bridge_quarantine`, verify that the entry's `session_id` matches the completing session before clearing the entry.

## Capabilities

### Modified Capabilities
- `http-bridge`: Protect retry circuits from stale cleanup deletion across concurrent claims, and prevent cross-session quarantine clearing.
