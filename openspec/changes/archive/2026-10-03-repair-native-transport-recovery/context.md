# Native transport audit batch

Exactly three source-registry tasks: UP-ISSUE-2471, UP-ISSUE-2470 and UP-ISSUE-2456. Base source is `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`; corrections are local working-tree changes, not a new source SHA, release or production deployment.

The fresh upstream [#2456](https://github.com/Soju06/codex-lb/issues/2456) report explicitly rescopes recovery to IOCP route errors 1231/1232 and retains reset/timeout 64/121 endpoint attribution. The historical ISSUES.md excerpt omitted that revision. Four unit and four route cases failed against the old classification before the correction.

For [#2471](https://github.com/Soju06/codex-lb/issues/2471), existing account pool isolation passes actual TLS HTTP/2 tests. A control that removes the IPC pool key reproduces both-account collateral failure. A separate defect was confirmed: native body-read phase is recorded in the core client but disappears before request-log persistence. Six actual routes initially stored null failure_phase. The new typed attempt trace preserves phase/detail/category/status while leaving event bytes and replay decisions unchanged.

For [#2470](https://github.com/Soju06/codex-lb/issues/2470), existing nested cleanup passes source-built-helper/route/real-database checks. Two failures followed by success at stream limit one are sufficient to expose even a single leaked lease; running a longer streak could introduce intentional health cooldown, a different condition. Canonical non-stream collection and backend native JSON are exercised according to their distinct existing upstream contracts.

The broader #2471 raw error-chain/cf-ray and per-request WebSocket-preference asks remain unaudited. A pre-header POST failure does not prove non-dispatch, so ambiguous replay remains forbidden. macOS offload behavior, physical Windows route loss, hosted provider/client traffic, public artifacts and cloud gates are not certified here.

The old completed active change `recover-windows-transport-failures` remains historical and contains superseded 64/121 semantics. Its delta must not be blindly archived over the corrected main requirement. This batch changes the current SSOT and records the new overriding requirement without altering unrelated historical artifacts.
