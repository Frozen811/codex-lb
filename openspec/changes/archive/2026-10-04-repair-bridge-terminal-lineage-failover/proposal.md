## Why

Three unchecked registry items (#2493, #2465, #2455) describe failures at HTTP bridge continuation boundaries. Verify the actual route contracts and repair any remaining defects without weakening account ownership or replay safety.

## What Changes

- Prove denied proxy anchors produce one actionable terminal result before and after SSE commitment.
- Prove eventless sticky lineages can recover with a verified fresh transcript, and image/tool requests obey Responses-Lite normalization.
- Prove payload-budget fallback permits quota failover only after API-key-scoped durable full-resend verification.
- Add route regressions, repair uncovered defects, synchronize requirements/context, and close exactly these three registry rows with evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: terminal delivery, sticky lineage recovery and verified quota failover at HTTP bridge boundaries.

## Impact

HTTP bridge streaming and upstream-event processing, direct HTTP retry, Responses HTTP ingress, targeted integration/unit tests, and the local issues-check registry. No new settings, migrations, dependencies or release actions.
