## Why

The audit registry has no independent evidence for UP-PR-2540, UP-PR-2541, and UP-PR-2545. Existing helper tests do not establish that malformed legacy planner times remain editable, unusual declared SCIM lengths cannot crash admission, or a failed publication after an operator mutation eventually reaches a peer.

## What Changes

- Verify clock validation and legacy read/correction through the planner API; fix any response validation that blocks correction.
- Bound SCIM declared-length admission without unbounded integer conversion, preserve streaming limits, and verify POST/PUT/PATCH refusal without mutation.
- Exercise failed immediate invalidation through operator routes and real database-backed peer caches, including cancellation and recovery.
- Record independent evidence and close exactly these three registry entries locally.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `quota-phase-planner`: explicitly preserve malformed legacy clock strings on read and partial correction.
- `http-ingress-limits`: define safe SCIM declared-length validation and oversized decimal admission.

## Impact

Planner response schemas, SCIM resource body reader, targeted API/cache integration tests, owning specs/context, and issues-check.md. No new settings, dependencies, migrations, publication, or deployment. Existing cache invalidation requirements remain unchanged.
