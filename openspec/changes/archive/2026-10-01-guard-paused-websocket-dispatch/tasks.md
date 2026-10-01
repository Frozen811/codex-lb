## 1. Reproduction

- [x] 1.1 Trace Pause mutation, routing markers, bridge/direct socket reuse and quota surfaces; record the clarified user observation in context.
- [x] 1.2 Add public WebSocket regressions with real account selection and Pause; demonstrate failure before the guard.

## 2. Implementation

- [x] 2.1 Guard new response.create at the final dispatch boundary using the existing marker; verify both public surfaces and anchored/unanchored turns.
- [x] 2.2 Prove delayed-admission cleanup and preservation of already-dispatched work with regression tests and reservation checks.

## 3. Verification and records

- [x] 3.1 Run focused direct socket, passthrough, pooled usage and cross-replica Pause checks; verify Ruff, architecture and strict OpenSpec.
- [x] 3.2 Update issues-check and main context with evidence and unresolved quota/client limits; sync and archive after verification.
