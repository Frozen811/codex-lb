## Why

The independent registry still lacks evidence for UP-ISSUE-2169, UP-ISSUE-2108, and UP-ISSUE-2074. HTTP phase sampling currently counts local failures and non-event SSE blocks, and the main bridge spec contains contradictory post-output account-health requirements.

## What Changes

- Observe HTTP upstream phases only from real upstream events, preserving zero and keeping missing phases null.
- Verify the closed-port native SSE/compact fallback fixture without weakening its deadlines or no-replay assertions.
- Verify post-output bridge drops, protocol/authored-close controls, and reconcile the obsolete eventless-only requirement with the current contract.
- Record focused regression evidence and close exactly these three registry items for verified local scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `proxy-runtime-observability`: HTTP phase observations exclude local events and keepalives and distinguish real upstream events with synthesized IDs.
- `responses-api-compat`: reconcile abrupt-drop requirements while preserving replay and eventless drain rules.

## Impact

`app/modules/proxy/_service/streaming/mixin.py`, targeted HTTP/bridge/native tests, the two owning specs and context documents, and `issues-check.md`. No schema, settings, metric families, dependency or routing changes.
