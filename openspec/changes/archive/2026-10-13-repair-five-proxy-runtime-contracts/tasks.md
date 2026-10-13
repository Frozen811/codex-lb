## 1. Runtime repair

- [x] 1.1 Fix UP-PR-2561 warm cap snapshots; verify keyed/unkeyed public routes, cap updates, partitioning and cancellation cleanup.
- [x] 1.2 Fix UP-PR-2308 pooled quota egress; verify HTTP, bridge, source SSE, both native WebSocket paths, privacy, raw ingestion and unavailable metadata.

## 2. Existing contracts

- [x] 2.1 Independently verify UP-PR-2112 HTTP phase timing/provenance through existing public route and metric tests.
- [x] 2.2 Independently verify UP-ISSUE-2343 pending/drained/unknown observation and callback handoff ownership through loopback drain status tests.
- [x] 2.3 Independently verify UP-ISSUE-2505 bounded database work completion, tracked fallback and lease release, including available isolated process tests.

## 3. Completion

- [x] 3.1 Run focused runtime tests, static guards and strict change/canonical spec validation; synchronize specs/context and archive exact evidence.
- [x] 3.2 Update/reread exactly five selected registry rows, verify other333 rows and unrelated dirty files against the initial manifest, and inspect the final full batch diff.
