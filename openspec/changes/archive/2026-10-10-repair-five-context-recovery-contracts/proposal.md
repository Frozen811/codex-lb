## Why

The HTTP bridge omits unanchored root turns from its operation ledger, leaving durable replay chains without their original context. Five unverified registry records also need current product-path evidence for developer context, prewarm anchors, subagent resends and clean-close handoff.

## What Changes

- Persist root HTTP bridge turns under the same owner, payload-size, duplicate and cleanup fences used for continuations.
- Reject incomplete or mismatched durable terminal evidence before exposing a replay chain.
- Verify context preservation and queued WebSocket receive ownership at the public routes, with negative controls.
- Close exactly UP-ISSUE-1898, UP-ISSUE-2563, UP-ISSUE-2574, UP-ISSUE-2582 and UP-ISSUE-1304 in supported local scope.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: root operations and verified terminal evidence are required for complete durable replay transcripts.

## Impact

HTTP bridge request submission, durable transcript loading, replay validation, focused Python tests, OpenSpec and issues-check.md. No configuration, dependency, schema or dashboard change. Per-dispatch generation fencing (UP-PR-2579) is outside this batch.
