# Verification: native transport recovery

Source base: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`, Windows x64, Python 3.13.12, Rust 1.96.0. Changes remain local and uncommitted. Only UP-ISSUE-2471, UP-ISSUE-2470 and UP-ISSUE-2456 were selected.

## Completeness and correctness

| Requirement | Implementation/evidence | Result |
|---|---|---|
| Windows typed route recovery | `network_recovery.py`, updated unit and transient-retry regressions; six real shared-generation route cases | PASS |
| Native account pool isolation | Existing Python IPC `pool_key=account_id` and Rust `ClientKey`; actual TLS HTTP/2 account pools plus shared-pool control | PASS |
| Native failure diagnostics | Attempt-owned `UpstreamResponseFailureTrace` in core client, consumed by `_stream_once` before persistence | PASS |
| Direct failure cleanup | 18 actual route/helper/real-database cases, each with two failures and a final successful request under stream/create caps of one | PASS |

All four changed requirement blocks and every scenario match the synchronized main specs. No new setting, dependency, schema, release gate bypass or replay eligibility was added. Failure trace contains only typed phase, a static category and observed status; external SSE bytes retain their existing contract. Existing stronger terminal/cancellation failure metadata keeps precedence.

## Red-before evidence

- Windows: two 1231/1232 classification cases, two 64/121 refusal cases and four actual route cases failed against the previous error set: **8 failed**. After the correction the same focused run was **11 passed**.
- Native diagnostics: six body-failure route variants stored `failure_phase=None` before the attempt trace was added: **6 failed**. Afterward body-read phase, `native_transport_error`, exception category and observed HTTP 200 persist; the six pre-head failures preserve phase `request` and no invented status.
- Pool control: stripping the IPC pool key causes A/B to share one physical HTTP/2 connection and both fail when it is aborted. With account pools, A reuses one connection for three requests while B completes on another; no ambiguous POST is resent.

## Validation commands

Final-source Python validation:

- `uv run --frozen pytest -q --timeout=30 tests/integration/test_native_transport_contracts.py tests/integration/test_native_sse_egress.py tests/unit/test_native_egress.py tests/unit/test_http_client.py tests/unit/test_network_recovery.py tests/integration/test_proxy_transient_retry.py -k 'not native_http_terminal_releases_upstream_without_python_cancel' --tb=short`: **595 passed, 12 deselected**, 172.75 seconds.
- Each of the 12 deselected native terminal cases was run in its own fresh process with `--timeout=20`: **12 x 1 passed**, no skips.
- With the separate 17-case selector below: **624 distinct Python cases passed**. This is split-process coverage, not a claim that the full combined run passed.

Separate focused `test_proxy_utils.py` selector (`stream_responses_raw_route_oserror or native_codex_stream or native_giveup or native_egress or ambiguous_native_failure`): **17 passed**.

New `tests/integration/test_native_transport_contracts.py`: **26 passed**. It checks six shared-generation Windows cases, two real HTTP/2/control cases, and 18 direct request variants. The latter issue 54 actual upstream POSTs, verify zero admission pressure after each, drained persistence, settled/released real reservations, helper stream cleanup, and success without restart.

Native prerequisite: source-built `target/debug/codex-lb-native-egress.exe`, SHA-256 `019142892DE956AA904BDA69759B84CAB283912A9BE8919C3C9AA03815E48B81`. It is supplied using `CODEX_LB_NATIVE_EGRESS_TEST_BINARY`; the wire probes executed, not skipped.

`cargo test --locked -p codex-lb-egress -p codex-lb-egress-worker`: **25 passed** (17 library + 6 HTTP protocol + 2 WebSocket protocol tests).

Ruff check and format check across all seven touched Python files: **PASS**. Proxy architecture and simplicity budget checks: **PASS**. OpenSpec 1.11.0 strict change validation: **PASS**; main specs: **68 passed / 0 failed**. `git diff --check`: **PASS**. Hash comparison confirms all **19** pre-existing modified files outside the registry remain byte-identical.

## Coherence, audit limits and residuals

No blocking implementation/spec mismatch was found in the separate final diff and scenario review. The refreshed graph still omits the new trace symbol; current source and actual routes establish its data flow. Graph completeness is not claimed.

One unconstrained aggregate rerun stalled and was interrupted. The combined timeout30 rerun timed out on the existing native terminal probe; a grouped 12-case selector also timed out on a routed terminal case. Each of those 12 cases passes in its own fresh process. The remaining 595-case bounded run passes. The group/session-lifecycle cause was not isolated, so wider aggregate stability/CI-04 remains open. An earlier pre-trace aggregate pass (597 cases) is historical, not the final-source gate.

UP-ISSUE-2470 is locally verified and closed. UP-ISSUE-2456 is locally corrected/closed against the fresh revised report. UP-ISSUE-2471 closes account-pool isolation and fixes typed persisted diagnostics locally, but remains **partial** for raw error-chain/cf-ray disclosure and per-request WebSocket-preference audit. A missing response head is insufficient proof for automatic POST replay; the documented safety invariant remains enforced.

Physical Windows adapter/route-loss injection, macOS TCP offload behavior, hosted provider/client traffic, deployed database topology, public artifacts and new cloud gates were not certified. The historical active `recover-windows-transport-failures` delta still contains superseded 64/121 semantics and must not be blindly archived over current SSOT. No commit, push, release, workflow dispatch or deployment was performed.
