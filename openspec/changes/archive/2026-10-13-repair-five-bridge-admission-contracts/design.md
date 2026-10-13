## Context

See proposal.md for motivation and the exact five records. The registry snapshot starts at HEAD `7e3779ffaea1a27c29710a7d496e8fa037131f98` with 457 dirty files. Those changes remain authoritative inputs and are preserved.

## Goals / Non-Goals

**Goals:** Preserve per-key creation ownership through failure and consistent conservative quota estimates through late anchor injection. Verify existing handoff recovery, backlog fairness and capacity handling using deterministic lifecycle and public ingress tests.

**Non-Goals:** Dispatch-generation schema work (UP-PR-2579), cross-account replay of opaque or visible-output requests, unbounded retry beyond existing deadlines, production performance certification and publication.

## Decisions

1. Cancel only the task captured on the matching inflight future while the registry lock is held. Do not await under that lock: the creator's existing failure funnel needs it to release resources. Matching the future protects replacement creators; handoff futures and the current task retain their existing ownership.
2. Update the request-local budget after successful reservation reconciliation. The existing opaque-input normalization remains the admission policy. Changing only the database reservation leaves subsequent stream-lease estimates stale; changing estimator constants or adding configuration would expand scope.
   The route regression also exposed a broad ledger exception handler that rewrites the deliberate late-anchor 429/401 into a persistence 502 and retires the healthy session. Preserve only typed local pre-dispatch refusals through this handler; genuine persistence failures retain their existing fail-closed path.
3. Exercise real disposable SQLite reservations before upstream send and prove refusal never dispatches. Add cancellation and stale-slot controls. Use both spool formats and public HTTP/bridge/native WebSocket regression paths.
4. Preserve the fork's replay-safety policy for UP-ISSUE-1935. Its request for arbitrary unbounded replay is incompatible with the canonical prohibition on repeating ambiguous HTTP POSTs or output-bearing turns. Record separately what is verified locally and what remains unimplemented in that original proposal.

## Risks / Trade-offs

- Cancellation is cooperative; existing registry and durable owner fences remain required for a creator that delays cancellation.
- A quota reconciliation failure must retain its external auth/rate-limit envelope and release the original reservation; local estimates must not authorize dispatch after refusal.
- Unit and loopback tests do not prove the incident on the reporter's deployment or real upstream goal/client retry behavior.
