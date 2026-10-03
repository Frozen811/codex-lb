## 1. Planner clock times — UP-PR-2540

- [x] 1.1 Reproduce malformed legacy clock read/correction through settings and forecast APIs, preserving strict invalid-write and atomicity assertions.
- [x] 1.2 Fix legacy response validation and verify partial correction, omitted/null fields, boundaries, and invalid clock regression tests.

## 2. SCIM bodies — UP-PR-2541

- [x] 2.1 Reproduce unsafe declared-length admission with external SCIM POST requests and verify no body consumption or database mutation.
- [x] 2.2 Fix bounded declared-length admission and verify POST/PUT/PATCH stream crossings, false lengths, leading zeroes, and exact-limit valid bodies.

## 3. Cache publication — UP-PR-2545

- [x] 3.1 Verify failed/cancelled immediate publication after operator Pause with real database state, pending retry, and independent peer routing cache convergence.
- [x] 3.2 Run targeted poller/bus cancellation, commit-ambiguity, marker interleaving, and namespace isolation regressions; repair any reproduced defect.

## 4. Completion

- [x] 4.1 Run focused tests, Ruff, strict OpenSpec validation, and an independent second source/scenario review; record exact evidence.
- [x] 4.2 Synchronize normative specs and context, mark exactly three own registry rows locally closed with evidence, and archive only after verification.
