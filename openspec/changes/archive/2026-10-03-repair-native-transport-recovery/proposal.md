## Why

The registry claims UP-ISSUE-2471, UP-ISSUE-2470 and UP-ISSUE-2456 are resolved without independent product-path evidence. The current upstream Windows report was rescoped to route errors 1231/1232, but the fork classifies peer reset/timeout 64/121 as process-wide failures instead.

## What Changes

- Restore Windows/POSIX route-failure parity using typed Windows route errors, preserving connector-only replay and shared-client generation ownership.
- Verify account-partitioned native HTTP/2 pools through the actual helper and a controlled TLS HTTP/2 origin.
- Preserve typed native failure phase, exception category and observed HTTP status in request logs without exposing raw transport details on the wire.
- Verify direct HTTP failures release account leases and API-key reservations before subsequent admission.
- Record exact local evidence and explicit remaining upstream/public/platform scope in the registry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `outbound-http-clients`: Windows route classification and account-partitioned native HTTP pools.
- `responses-api-compat`: deterministic direct-stream cleanup after native transport termination.

## Impact

`app/core/resilience/network_recovery.py`, `app/core/clients/proxy.py`, `app/modules/proxy/_service/streaming/mixin.py`, existing Windows recovery unit/integration tests, a new native transport integration suite, owning OpenSpec specs/context, and `issues-check.md`. No new runtime setting, dependency, migration, publication or deployment.
