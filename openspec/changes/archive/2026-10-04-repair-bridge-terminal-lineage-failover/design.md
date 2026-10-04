## Context

See proposal.md for the three registry items. The bridge already has durable transcript verification, replay/circuit fencing, late-terminal delivery, and Responses-Lite projection. Integration tests are excluded from the code graph, so their coverage is inspected directly. Existing checkout edits are preserved using an initial file snapshot.

## Goals / Non-Goals

Prove the three issues through public HTTP routes, including negative ownership and partial-failure cases. Keep current account/session/task owners and bounded retries. Hosted acceptance, published artifacts and production are separate verification scopes.

## Decisions

- Exercise real service and SQLite repository paths; use deterministic local upstreams for wire evidence. Helper tests alone cannot prove SSE delivery or durable ownership.
- Repair only confirmed failures. Reuse existing transcript proof and cleanup/finalization paths rather than introducing settings or another registry.
- Count SSE commitment separately from output visibility. Keepalives commit a response without making replay safe or unsafe by themselves.
- Keep durable full-resend verification API-key scoped and compare resolved ownership before dropping affinity. Explicit anchors, files, incomplete histories and forwarded ownership remain protected.

## Risks / Trade-offs

- Circuit and quarantine races can escape a happy-path regression; targeted existing fence and cancellation suites supplement route checks.
- Local deterministic upstreams do not reproduce vendor overload rates or cache-hit percentages; record this limit explicitly.
- An old unsafe full-resend unit fixture mocked only the durable lookup. Its owner-retirement path reached a real uninitialized SQLite repository. Stub the retirement boundary with a non-retiring answer and assert the expected owner; keep the production refusal and real-DB route tests intact.

## Migration Plan

No data migration or configuration change. Preserve earlier edits and archive only after focused runtime, static and strict specification checks pass.
