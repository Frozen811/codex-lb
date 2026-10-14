## Why

Five open registry rows need independent product-path evidence. Strict model routing headers currently do not reach account selection, and child affinity TTL does not bound the retained HTTP bridge socket and stream lease.

## What Changes

- Carry strict model routing through HTTP Responses, compact, native WebSocket and HTTP bridge selection, refusing conflicts with required owners.
- Bound child bridge idle retention by its effective affinity TTL while preserving established ownership.
- Apply child diversification when a transport labels an account-neutral fresh child as a follow-up.
- Independently verify probe recovery, parent-account diversification and revoked-token retirement, adding negative boundary coverage where missing.
- Update exactly UP-ISSUE-2327, UP-ISSUE-1576, UP-ISSUE-1307, UP-PR-2448 and UP-PR-2117 in issues-check.md.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-routing`: strict routes are enforced on transport entrypoints and cannot override required stored-object or file ownership.
- `sticky-session-operations`: child HTTP bridge retention follows the bounded child affinity lifetime.

## Impact

Proxy selection, streaming/compact/WebSocket/HTTP bridge call sites and regression suites. No schema, settings, setup, dashboard rendering or dependencies change. Evidence is local; publication and live-provider validation are separate.
