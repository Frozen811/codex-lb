## Why

Exactly five open local registry rows describe threads stranded on invalid response anchors or unavailable owners: UP-ISSUE-1921, UP-ISSUE-1707, UP-PR-2423, UP-PR-2467 and UP-DISC-1864. Existing recovery fixes need independent verification across public transports. Request-path owner retirement currently treats an incidental reset timestamp on a paused, deactivated or unusable reauthentication owner as evidence of automatic recovery, leaving a dead client anchor retryable.

## What Changes

- Use a reset deadline as a recovery horizon only for rate-limited or quota-exceeded owners.
- Specify and verify actionable dead-client-anchor rejection, idempotent retirement and subsequent anchor-free recovery.
- Specify and verify exact retirement of tombstoned proxy-injected anchors, keeping delta-only and concurrent-successor protections.
- Verify existing invalid-anchor normalization and full-context recovery through HTTP, HTTP bridge and native WebSocket routes.
- Update exactly the five selected registry rows with local evidence and explicit external limits.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: dead-owner recovery horizons, client-anchor rejection and submit-time proxy-anchor tombstone retirement.

## Impact

Application changes are limited to `app/modules/proxy/durable_bridge_repository.py`, `app/modules/proxy/_service/http_bridge/streaming.py` and `app/modules/proxy/_service/http_bridge/request_submit.py`. Public-route regressions also exposed an already-retired lookup returning the old retryable 502 on the second client-anchored request, and a submit-time tombstone refusal transformed into a missing-operation-fence 502 by attempted transparent recovery. Preserve the authoritative retirement verdict and the local undispatched refusal. Tests cover real SQLite state and public Responses paths. No schema, setting, dependency or dashboard change. Preserve existing dirty work; no publication or deployment.
