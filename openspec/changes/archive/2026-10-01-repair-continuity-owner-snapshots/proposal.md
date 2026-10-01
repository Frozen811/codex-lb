## Why

The fork's continuity fallback returns session-owned Account rows and reads them after teardown, causing DetachedInstanceError on Responses and compact owner misses. Its sole-owner fallback also differs from the recorded fail-closed spec and leaves required architecture gates failing.

## What Changes

- Snapshot candidate accounts while their repository session is open and use the typed API-key assignment scope.
- Define the bounded sole-possible-owner exception described in upstream issue #2274: successful lookup miss, exactly one subscription account in the allowed scope, then normal owner-bound admission.
- Preserve refusal on lookup errors, ambiguous/empty scopes, conflicting ownership and unavailable required owners.
- Place shared fallback resolution in the service support domain and move required-owner policy validation into the existing load-balancer selection domain without increasing architecture ratchets.
- Add real-session and public HTTP/compact/WebSocket regression coverage; record artifact provenance separately in issues-check.md.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: clarify hard continuity owner lookup, sole scoped candidate fallback, snapshot lifetime and admission restrictions.

## Impact

LoadBalancer candidate snapshots and required-owner policy validation; shared service support; HTTP streaming retry, compact and direct WebSocket callers; continuity unit and product integration tests. No schema, dependency, settings or release changes. Docker latest provenance, Pause investigation and unrelated CI failures remain separate audit work.
