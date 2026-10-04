# Verification

Date: 2026-10-03. Base HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`.
Exactly UP-ISSUE-2425, UP-ISSUE-2081 and UP-ISSUE-1208 were selected. The result
is local and uncommitted; no push, release, deployment or external message.

## Completeness and correctness

| Requirement / scope | Implementation and observable evidence |
|---|---|
| Inline image bridge, UP-ISSUE-2425 | Existing bounded admission; 69 unit/integration cases, including both HTTP paths, text/image/text connection reuse, valid PNG identity, output-free overload recovery, caps, unsupported shapes, rollback and cancellation. The raw fallback is guarded against during admitted flows. |
| Direct ending provenance | Typed default-false adapter field; incomplete Python handshakes, closed routed sockets and native transport phase confer positive ending evidence. 20 v1/backend route controls distinguish None/1006 closes, confirmed error endings, unproven errors and authored 1011. Reasoning/text progress causes no replay. Ten adapter cases exclude protocol and open-socket errors. |
| Native reset without handshake | Actual loopback socket abort fails the original helper classification and passes after the specific Rust variant gains transport phase. The native and Python adapters both report positive terminal evidence. Other native protocol errors retain protocol phase. |
| Selected owner terminal | Four v1/backend error/response.failed route cases preserve original sanitized code/type/message/param/plan/reset metadata and 429 status when supplied. One upstream dispatch, one log and one health call. Unit owner/file-bound regressions confirm finalizer handoff and no early classifier health write; the existing settlement/cancellation suite covers finalization ownership. |
| Native JSON body encoding | Scoped native Responses/compact POST opt-in; level-3 zstd precedes stream registration and IPC dispatch. TLS H2 origin observes repeated deterministic bytes, exact decoded JSON, matching encoded length, absent implicit request identity/negotiation headers, preserved native identity and 2 MiB/5 MiB windows. |
| Body boundaries | Real H2 controls verify opaque bytes and stale Content-Encoding/Content-Length replacement. Routed JSON/compact opt-in, multipart exclusion and original Python fallback JSON/headers are tested. Direct/routed native compact and cancellation suites execute the actual helper. |
| Bounded native transport profile | Existing reqwest/Rustls configuration and normalized SDK identity are retained. The normative fingerprint-divergence promise and the source claim of complete header-order parity were corrected to measured guarantees and explicit limitations. |

## Reproductions before fixes

- Four direct route cases wrongly wrote account health for a positively ended
  error-kind socket. Both reasoning and visible-text progress reproduced it.
- A selected-owner error-kind quota event returned `upstream_unavailable` and
  owner-unavailable text rather than its authentic 429 and reset metadata.
  The file-bound unsafe-switch unit fixture encoded the same wrong contract.
- The real native WebSocket abort lacked ending provenance because
  ResetWithoutClosingHandshake used the generic protocol phase.
- The TLS HTTP/2 origin saw no request Content-Encoding for native JSON.

The first expanded route fixture accidentally used a fictional account and
counted created-only replay frames. It was corrected to a committed Account and
buffered reasoning/text progress before recording the four health failures.
A response.failed fixture lacked response.created correlation and waited for an
unmatched response; adding its accepted lifecycle corrected that fixture.
Neither harness failure is presented as a product defect.

The initial compression regression run had 24 failures because the old local
origin handlers parsed encoded bytes as plain JSON. Origin dispatch now decodes
zstd according to the actual wire header, while retaining wire headers and the
raw-reader interface. Actual H2 capture independently checks encoded bytes.
All affected native cancellation/admission cases pass with that origin behavior.

## Final validation

**797 distinct Python cases passed**, counted without duplicate reruns:

- Adapter/native/Codex/fingerprint/cancellation unit files: **274 passed**.
- Inline-image unit and public/backend route files: **69 passed**.
- Direct terminal route matrix: **24 passed**.
- `test_proxy_utils.py` selected WebSocket processing/security/settlement cases:
  **69 passed**. The combined selector was 72 including three Codex fallback
  cases already counted in the 274 unit run.
- Native wire, transport and SSE suites: **349 passed, 12 deselected**.
- The twelve native terminal cleanup cases were each run in a fresh process
  against the final helper with timeout20: **12 x 1 passed**, no skips.

Representative commands:

```
uv run --frozen pytest -q --timeout=20 tests/unit/test_websocket_terminal_provenance.py tests/unit/test_proxy_websocket_client.py tests/unit/test_websocket_terminal_cancellation.py tests/unit/test_codex_client.py tests/unit/test_native_egress.py tests/unit/test_proxy_upstream_fingerprint.py
uv run --frozen pytest -q --timeout=20 tests/integration/test_http_bridge_inline_images.py tests/unit/test_http_bridge_inline_image_admission.py
uv run --frozen pytest -q --timeout=20 tests/integration/test_direct_websocket_terminal_evidence.py
uv run --frozen pytest -q --timeout=20 tests/unit/test_proxy_utils.py -k 'process_upstream_websocket_text or websocket_keeps_previous_response_pinned_security_work_error or websocket_terminal_hands_log_off_before_health'
uv run --frozen pytest -q --timeout=20 tests/integration/test_websocket_terminal_wire.py tests/integration/test_native_transport_contracts.py tests/integration/test_native_sse_egress.py -k 'not native_http_terminal_releases_upstream_without_python_cancel'
cargo test --locked -p codex-lb-egress -p codex-lb-egress-worker
cargo build --locked -p codex-lb-egress-worker
```

Native commands use `CODEX_LB_NATIVE_EGRESS_TEST_BINARY=target/debug/codex-lb-native-egress.exe`.
Final helper SHA-256:
`BBD2BB52E5FE9989151E245A5CA7E3A280D292C304B2540EC68417973205466D`.
Rust checks: **25 passed**; formatting check passes.

Ruff check/format for the thirteen touched Python files, scoped `ty` for the
four changed client/relay files, proxy architecture, cancellation safety,
timing seams and simplicity budgets pass. Strict change validation passes;
verified archive synchronized two added requirements and one modified requirement.
Main specs strict validation: **68 passed, 0 failed**. Registry validation confirms
66 unique F rows, all three updated entries, complete archived tasks and valid
repository-relative evidence links; historical external attachment paths are
outside this link check.

Baseline hashes covered 57 pre-existing dirty/untracked files. Eight shared task
paths were intentionally updated; all **49 other paths remain byte-identical**.

## Coherence and residual scope

The final source and diff were reviewed against each requirement separately from
the implementation pass. Unsafe migration only disables replay; it no longer
rewrites a dispatched owner's error. Positive ending evidence affects account
health, not authorization to duplicate an already-dispatched request. Compression
is internal opt-in and does not mutate fallback headers, add settings, alter
reservations or change opaque relay representation. No new blocking mismatch
remains in the verified local scope. Context and the three registry rows were
updated alongside the corrected ISSUES.md claims.

Code graph navigation identified the Python producers/consumers and tests. Rust
call edges were incomplete, so current source and real helper wire tests establish
that path. Fast index refresh returned indexed status but still omitted the renamed
unit-test symbol (reported graph counts also differed from its expected counts).
Current filesystem and runtime evidence remain authoritative; fresh complete
graph coverage is not claimed.

The twelve historically unstable grouped terminal cases were intentionally run
in separate fresh processes. This is split-process coverage, not aggregate-suite
stability certification. CI-04 and its unresolved group lifecycle cause remain
open. Existing AsyncMock archive warnings and the Starlette deprecation warning
are recorded; no skipped native probe is counted as executed evidence.

UP-ISSUE-2425 and UP-ISSUE-2081 are locally closed. UP-ISSUE-1208 is locally
corrected and partially verified: full real-client header order, TLS ClientHello
comparison and fingerprint indistinguishability were not established. Hosted
image/overload rates, provider acceptance of compressed requests, deployed
artifacts, exact-head cloud gates and production traffic require separate evidence.
