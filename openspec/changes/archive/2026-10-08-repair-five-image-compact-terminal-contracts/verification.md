# Verification: five image, compact and terminal records

Date: 2026-10-08, Europe/Kiev. Base main: `8369ec720c5ac935f7a64fe3f30aa1cbc323f5e5`. Exactly five selected rows, initially НЕ ПРОВЕРЕНО: **UP-PR-2503 / UP-PR-2534 / UP-PR-2451 / UP-PR-2317 / UP-PR-2319**. The initial checkout already contained the completed section-69 auth/credit package; it was backed up before edits.

## Current upstream evidence

Live GitHub REST bodies and heads were read before implementation. These are source snapshots, not claims of merge readiness.

| Record | Current source head | State |
|---|---|---|
| [2503](https://github.com/Soju06/codex-lb/pull/2503) | `560a00b64127bc1769e0a1e51aa90aeacbfb1390` | Open |
| [2534](https://github.com/Soju06/codex-lb/pull/2534) | `f222787fe1e07d34fe93ec55d6af5adb67b6c133` | Open |
| [2451](https://github.com/Soju06/codex-lb/pull/2451) | `b4571cdf7d30ce123d2514d6e7075b62fd20b929` | Open |
| [2317](https://github.com/Soju06/codex-lb/pull/2317) | `a872ec980739afcbdec5e31b2e88e5c724ac4b07` | Open |
| [2319](https://github.com/Soju06/codex-lb/pull/2319) | `26cfb9e8b18b3391a78c46877fe7e6be85f25aed` | Open |

UP-PR-2324 was considered before the final selection but is not selected, implemented or closed. Its external compact-forwarding proposal conflicts with the fork's current explicit source-compaction refusal. The current owning spec and exact five selected records govern this package.

## Findings and resolution

- **2534 — fixed:** the encoded-length shortcut classified malformed over-bound PNG/JPEG base64 as `image_too_large`, violating unsupported-shape precedence and misreporting padded decoded sizes. A compiled character class checks the original string at the prefix offset, with quartet/padding validation and no full-segment copy or decode. Legal oversize still rejects before send. Unit coverage exercises punctuation, whitespace, URL-safe/non-ASCII characters, bad padding, both sibling orders, accurate sizes and the real 6,666,668-character bound. Both public Responses routes exercise top-level and nested tool-result shapes and a successful next text turn. Existing default-on, exact 5 MB admission, final 64 MiB frame, connection/image retention, rollback, close-1009, cancellation and accounting cases pass.
- **2503 — verified and documentation synchronized:** replayed images retain the bridge under the current default-on bounded contract, which supersedes the earlier current-turn-only exception. Raw-attempt logs and decision counters already use concrete `http`/`websocket` labels while the client keeps its `auto` fallback mode. Three new regressions verify those labels/modes; stale normative `auto` log wording was corrected. Historical/current image, external URL, promotion and repeated-connection tests pass.
- **2451 — fixed compatibility gap and documentation:** existing canonical source-compaction refusals were correct. Both explicit trailing-slash routes returned 405 instead of reaching their handlers. Hidden aliases now preserve the same dependencies and contracts without a redirect. Enabled/disabled sources on the three canonical route families, slash forms, assigned limited API keys, registry-shadow negative controls and native success/header controls pass. Refusals precede selection, admission, reservation and dispatch and create no dispatch log. Stale source/disabled-source spec exceptions were corrected and the refusal requirement added. The two old tests asserting 405 now assert native `503 no_accounts` and retain the no-dispatch invariant.
- **2317 — existing implementation verified:** the configured default is 900 seconds with the existing upstream settlement reserve. Direct collection tests capture the independent 45-second SSE idle timeout without an override, shortened total/idle overrides and an override that cannot widen a configured 60-second total. The default automation reclaim derivation is 930 seconds; pinned larger budgets remain respected. Native compact routes, metadata, settlement, timeout and automation selections pass; no production timeout change was needed.
- **2319 — existing implementation verified and public coverage extended:** both Responses HTTP routes retain exactly one original terminal when post-terminal health persistence raises, with exception logging. Focused keyed/unkeyed stream and compact tests cover settlement-before-health, queued-write continuation after failure, cancellation, shutdown draining and owner-error preservation. Production health logic required no change.

## Red-before and final Python verification

```text
uv run pytest -q tests/unit/test_http_bridge_inline_image_admission.py tests/integration/test_http_bridge_inline_images.py -k 'oversized_malformed or oversized_legal' --tb=short --show-capture=no --timeout=30
```

Before production repair: **15 FAILED /1 PASS**, 8.55 seconds. After repair: **16 PASS**, 3.89 seconds. A later real-bound regression also passes in the final selection. Corrected source-refusal fixtures established a separate genuine trailing-slash defect: **4 FAILED /11 PASS** before aliases, then the source/native selection passed. Early fixture trials used an obsolete native model, the wrong disabled-field alias/error type or omitted required native instructions; they are not product failures or acceptance evidence.

Final disjoint main selection:

```text
uv run pytest -q -n 4 --dist loadfile tests/unit/test_http_bridge_inline_image_admission.py tests/unit/test_compact_deadline_contracts.py tests/unit/test_bridge_transport_labels.py tests/unit/test_timeout_invariants.py tests/integration/test_http_bridge_inline_images.py tests/integration/test_http_promotion_accounting.py tests/integration/test_source_compaction_refusal.py tests/integration/test_proxy_compact.py tests/integration/test_proxy_compact_triggers.py tests/integration/test_proxy_compact_hop_by_hop.py --tb=short --show-capture=no --timeout=45 --durations=5
```

**224 PASS**, no skips/xfails/failures, 78.94 seconds. Four workers use isolated test storage. The earlier expanded run had **222 PASS /2 FAIL** from legacy 405 expectations and is not claimed green; the final command rechecks the full selection after updating those contract assertions.

Additional disjoint selections:

| Command | Result |
|---|---|
| `uv run pytest -q tests/unit/test_proxy_utils.py -k '(compact and (budget or timeout or flush)) or (stream and (health or settlement or terminal or owner_rewrite))' --tb=short --show-capture=no --timeout=45 --durations=4` | 106 PASS |
| `uv run pytest -q tests/integration/test_automations_api.py -k 'budget or claim and (stale or fresh or timed_out)' --tb=short --show-capture=no --timeout=45 --durations=3` | 10 PASS |
| `uv run pytest -q tests/integration/test_api_keys_api.py -k 'compaction_trigger or compact and source' --tb=short --show-capture=no --timeout=30` | 2 PASS |
| `uv run pytest -q tests/integration/test_proxy_responses.py -k 'health_write_failure_keeps_one_terminal' --tb=short --show-capture=no --timeout=30` | 2 PASS |
| `uv run pytest -q tests/unit/test_native_egress_websocket_chunking.py --tb=short --show-capture=no --timeout=30` | 8 PASS |
| Current-source helper IPC selection below | 3 PASS |

Total: **355 distinct Python tests PASS**, with no skips/xfails. Intermediate/regression reruns are not added again. Warnings are the existing Starlette BlockingPortal deprecation. This is a focused acceptance result, not a full-repository test claim.

## Native helper acceptance

Cargo 1.96.0, Windows/MSVC, locked dependencies, source from this checkout. The Rust crate sources and Cargo lockfile are unchanged. Build output is outside the repository under `C:/Users/ext/AppData/Local/Temp/codex-five-compact-images-20261008/cargo-target`.

```text
cargo test --locked -p codex-lb-egress --target-dir C:/Users/ext/AppData/Local/Temp/codex-five-compact-images-20261008/cargo-target
cargo build --locked -p codex-lb-egress-worker --target-dir C:/Users/ext/AppData/Local/Temp/codex-five-compact-images-20261008/cargo-target
cargo test --locked -p codex-lb-egress-worker --target-dir C:/Users/ext/AppData/Local/Temp/codex-five-compact-images-20261008/cargo-target
```

**17 egress +8 worker protocol =25 Rust tests PASS**. These include coupled frame/message caps, over-16-MiB both-direction WebSocket relay, chunk reassembly, typed failures and cancellation. No ignored tests.

With `CODEX_LB_NATIVE_EGRESS_TEST_BINARY` set for the test process to that directory's `debug/codex-lb-native-egress.exe`:

```text
uv run pytest -q tests/integration/test_native_egress_helper_large_payload_ipc.py --tb=short --show-capture=no --timeout=60 --durations=3
```

**3 PASS**, 4.53 seconds: receive/reassemble and send messages larger than 25 MiB through the real helper, plus configured receive-cap rejection. Binary SHA-256: `E39AF46C5BE885BC77CAFF2B1E21CCF68F55A1669EE63DA731D2F359DAD1B774`. Synthetic loopback data, no provider traffic.

## Static, OpenSpec and preservation gates

Whole-repository Ruff and format: PASS, 1486 files. Scoped ty for both production modules and the new/changed standalone test modules: PASS. Proxy architecture, cancellation safety and timing seams: PASS, existing ratchets retained. Strict change and main-spec validation: PASS, main **68/68**. Final simplicity, rendered-docs, whitespace, requirement-sync and preservation readbacks are recorded after execution below.

The delta contains **five MODIFIED requirements and one ADDED requirement**. Existing scenarios were retained, stable rationale/examples were synchronized to capability context, and implementation/scenario mapping was checked. No unresolved implementation or correctness finding blocks archive. The scope adds no setting, dependency, schema, dashboard, README section or changelog edit.

Initial backup: `C:/Users/ext/AppData/Local/Temp/codex-five-compact-images-20261008/initial-manifest.json`, 19 files with SHA-256 hashes. Only the registry and the expanded public health test intentionally overlap that prior package; the auth/credit code, specs, tests and archive must otherwise remain byte-identical. Registry completion is limited to the five selected rows; the other 333 source records and the pre-existing partial/F-045/CI-04/external residuals remain intact.

Local Windows/SQLite/native-loopback acceptance does not certify Linux/macOS, live providers, PostgreSQL/MySQL runtime, cloud checks, public artifacts, releases or production. No commit, push, PR or deployment was performed.

## Final completion readback

- `uv run python .github/scripts/check_simplicity_budgets.py`: PASS, all five budgets; no surface additions.
- `uv run mkdocs build --strict --site-dir C:/Users/ext/AppData/Local/Temp/codex-five-compact-images-20261008/site`: PASS, 2.14 seconds.
- `npx --yes @fission-ai/openspec@1.11.0 validate repair-five-image-compact-terminal-contracts --strict`: PASS after synchronization.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict`: **68/68 PASS**.
- Exact normalized main/delta block parity: **6/6 requirements**. Existing scenarios retained.
- `git diff --check`: PASS.
- Prior dirty-file preservation: **17/17 byte-identical** outside the two intended overlaps. Full comparison of the existing public Responses test confirms only the health-route parameter/path extension; previous auth/credit tests and edits remain intact.
- Registry saved readback: exactly the five selected rows closed locally, **333/333 other source rows byte-identical**, **338 total /116 closed /7 partial /215 unverified**. The initial 19-file manifest and final preservation-readback JSON remain in the external backup directory.
- Related UP-ISSUE-2465 and UP-ISSUE-2033 already had local closure evidence and retain their saved states; broad HTTP/WebSocket cache-parity UP-ISSUE-2409 remains unverified. No sixth row was changed.

Completeness, implementation correctness and design coherence were checked against the five modified and one added requirement. New and changed scenarios map to the image, source-refusal, transport-label and deadline suites above; unchanged surrounding scenarios retain their existing contracts. All eight tasks are complete. Archive uses `--skip-specs` only because direct synchronization and exact parity were verified; validation is not skipped.
