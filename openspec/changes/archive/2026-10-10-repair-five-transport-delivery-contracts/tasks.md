## 1. Reproduce and implement the live-output bound

- [x] 1.1 Record the five selected rows, upstream metadata and dirty-file snapshot; verify exact initial statuses and hashes.
- [x] 1.2 Reproduce aggregate and blocked-producer overflow with small-budget tests before runtime edits.
- [x] 1.3 Bound queued and waiting payload, release on all lifecycle paths, and verify cancellation/detach/drain/reclamation tests.
- [x] 1.4 Route budget exhaustion through ordered downstream failure without cancelling the reader; verify prefix/failure/EOS and sibling progress tests.

## 2. Verify the other four selected contracts

- [x] 2.1 Verify UP-PR-1084 with producer-generated local hints, genuine upstream controls and HTTP/WebSocket capacity route tests.
- [x] 2.2 Verify UP-PR-2472 with native marked-terminal, no-marker, refusal, lease release and public route tests.
- [x] 2.3 Verify UP-PR-2457 with typed Windows route/reset/timeout parity, connector/raw dispatch and no-message-provenance tests.
- [x] 2.4 Verify UP-PR-2075 with post-output/buffered drops, eventless controls, protocol/close provenance and public SSE tests.

## 3. Finish the bounded local batch

- [x] 3.1 Sync requirements and context, run focused tests, Ruff/format/typing, guards and strict OpenSpec; record exact evidence and residuals.
- [x] 3.2 Update and reread exactly five source rows plus summary; verify all other rows and unrelated dirty files against the snapshot, then verify and archive the change.
