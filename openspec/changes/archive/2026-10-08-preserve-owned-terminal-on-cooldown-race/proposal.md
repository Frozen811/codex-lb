## Why

CI #81 passed the repaired browser setup but exposed a real post-submit terminal race: a `response.incomplete` opens the durable circuit before its payload reaches the downstream queue, so the startup cooldown check can replace an already-owned upstream terminal with HTTP 503. The real-route reason-only incomplete test passed in isolation but failed under cloud scheduling.

## What Changes

- Keep an upstream terminal owned by settlement or already observed from being replaced by the post-submit empty-queue cooldown guard.
- Preserve the existing rejection and cleanup for a submitted request without terminal evidence.
- Add deterministic ownership/observation unit controls and a real-route delayed-terminal regression while retaining circuit-count, receipt replay, reservation, and zero-pressure assertions.
- Record and publish the verified fix, then follow complete exact-head CI.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: post-submit circuit suppression preserves an already-owned upstream terminal.

## Impact

Planned edits: `app/modules/proxy/_service/http_bridge/streaming.py`, `tests/unit/test_proxy_http_bridge.py`, `tests/integration/test_bridge_retry_terminal_contracts.py`, the Responses spec/context, `issues-check.md`, and this change's artifacts. Existing account ownership, retry accounting, receipt identity, and settlement rules remain enforced. No sixth source task or new setting.
