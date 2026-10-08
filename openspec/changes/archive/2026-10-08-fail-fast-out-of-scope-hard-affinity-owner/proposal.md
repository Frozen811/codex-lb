## Why

CI #84 found an unstable error in the API-key-scope goal-restart control: a hard owner outside the allowed pool was polled for the entire 75-second request budget, so deadline timing alternated between hard-affinity saturation and request timeout. Selector exclusion metadata covers explicit retry exclusions but omits the caller's allowed-account filter. The test helper also supplies an incomplete SimpleNamespace where production requires Settings.model_copy.

## What Changes

- Include caller-declared allowed-account scope in the existing no-recovery-wait hard-owner exclusion proof.
- Fail closed with the existing hard-affinity error when that owner cannot be selected by the request's immutable pool; do not dispatch, retire, or rebind it.
- Preserve recovery waits for temporarily unavailable owners that remain inside scope.
- Use a complete Settings model in the sticky-session fixture, keeping its existing request budgets, and add no-wait/API/selector controls.
- Record/publish the repair and follow complete exact-head CI.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-routing`: a hard owner excluded by the caller's allowed account pool has no recovery wait.

## Impact

Planned edits: `app/modules/proxy/load_balancer.py`, `_load_balancer/sticky_selection.py`, `_service/support.py` metadata documentation, `tests/unit/test_load_balancer_concurrency.py`, `tests/integration/test_proxy_sticky_sessions.py`, account-routing spec/context, registry, and change artifacts. No new setting, schema, sixth source task, or weakened scope rule.
