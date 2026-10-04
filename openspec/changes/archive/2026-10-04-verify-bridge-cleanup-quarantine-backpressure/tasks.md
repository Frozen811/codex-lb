## 1. Scheduled retry cleanup

- [x] 1.1 Reproduce same-timestamp count changes and mixed-batch reselection through scheduled cleanup with real database rows.
- [x] 1.2 Fence the selected count and paginate each key once; verify stale-row and continuity controls.

## 2. Quarantine lifetime

- [x] 2.1 Verify replacement sessions, pruning and failures during awaited settlement through bridge completion tests.
- [x] 2.2 Verify existing quarantine ownership/recovery regressions and document any unexecuted policy boundaries.

## 3. Paused downstream delivery

- [x] 3.1 Reproduce retained buffers and cancelled waiter leaks; repair queue shutdown and verify ordering/cancellation.
- [x] 3.2 Verify paused/resumed HTTP delivery, failure on stall, independent progress and reservation cleanup; repair observed delivery defects.

## 4. Evidence and completion

- [x] 4.1 Run focused tests, scoped lint/type/architecture checks and strict OpenSpec validation; sync spec/context and complete a second manual review.
- [x] 4.2 Update exactly the three selected registry rows, summary and verification evidence; verify unrelated dirty files remain intact and archive the verified change.
