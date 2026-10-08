## Why

CI #82 passed every integration shard and the browser repair, but a direct WebSocket handoff regression timed out because a queued second turn was lost. The relay replaces a receive task merely because it is done; a receive that completes while the retired upstream is closing therefore gets discarded before its result is consumed.

## What Changes

- Create a downstream receive task only when no receive task is owned; consume an existing completed result once before replacing it.
- Add a deterministic clean-close barrier that makes the second turn complete during upstream retirement, retaining the original three-second bound and frame assertions.
- Preserve downstream disconnect, idle/drain, replay, cleanup, and account-health behavior.
- Publish the verified fix and follow full exact-head CI, recording the result in the registry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: completed downstream receive results remain owned across upstream handoff.

## Impact

Planned edits: `app/modules/proxy/_service/websocket/mixin.py`, `tests/unit/test_proxy_utils.py`, Responses spec/context, `issues-check.md`, and this change's artifacts. No new setting, migration, dependency, or sixth source task.
