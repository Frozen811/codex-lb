# Verification: five routing ownership contracts

Date: 2026-10-09, Europe/Kiev. Local main HEAD remains `005c8aa4d06be1d0d2f1ccdb2e0f90b725884f8e`.
Exactly UP-PR-2332, UP-PR-2469, UP-PR-2486, UP-PR-2458, and UP-PR-2001 were selected from their own initially unverified registry rows. No upstream branch was transplanted or merged.

## Source and preservation

[source-snapshot.json](source-snapshot.json) contains all 338 initial source rows, the 132-file dirty manifest and external backup location, and fresh GitHub REST metadata/heads. 2469 was merged upstream; the other four were open at the read. Upstream state and author verification are not treated as local verification.

| Source | Local outcome | Evidence and boundaries |
| --- | --- | --- |
| [2332](https://github.com/Soju06/codex-lb/pull/2332) | Existing implementation independently verified | Exact `model_not_found` is health-neutral. Real HTTP route tests preserve exhausted 404 envelopes and unrelated valid work; 10 WebSocket cases cover movable pre-created replacement, temporary preference, exhaustion, anchored fresh-body preparation, and required turn-state owners. Ordinary invalid-request controls remain non-retryable. |
| [2469](https://github.com/Soju06/codex-lb/pull/2469) | Fixed | File adapter now preserves explicit typed phase/replay evidence. A returned finalization poll disables replay for the entire operation even when the next refusal is individually pre-dispatch. New real-route 4-case first/late-poll and pinned/unpinned matrix; existing create/finalize/TLS/ambiguous/body/network matrix and direct client/unary controls pass. |
| [2486](https://github.com/Soju06/codex-lb/pull/2486) | Existing implementation independently verified | Existing hard-owner fallback is threaded through core, sticky retention and unbound selection. Four new public-selector boundaries combine transient backoff with active/paused/excluded/capped admission and verify counters and pressure. Existing healthy-sibling and persisted-unavailability controls pass. |
| [2458](https://github.com/Soju06/codex-lb/pull/2458) | Fixed | A matching durable full resend with known redundant reasoning prepares a validated projection and activates it only for pre-visible quota or persisted quota loss. Owner's original body/aliases remain intact. Retiring a turn-state owner re-derives affinity after removing aliases, preventing the old hard key from blocking B. Unknown reasoning, wrong prefix, healthy owner, non-quota failure, paused selection and independent files remain bound. Existing plain full-resend fork behavior is retained. |
| [2001](https://github.com/Soju06/codex-lb/pull/2001) | Fixed | Coded pre-visible quota rejection does not create a dispatch owner for known reasoning/compaction ciphertext-only state. The full remainder must pass the existing neutral replay gate. Ciphertext remains identical on replacement; literal/recognized reasoning rejection is health-neutral and emits one private provenance warning. Independent pins, unknown state, visible output, ambiguous failure phases, code-less bursts and existing dispatch owners remain bound. |

The implementation adapts the relevant source concerns to the current fork, including its stricter known-item validation and existing durable proof contracts. Source metadata retains author/context attribution. Unrelated migration and broad branch changes were not imported.

## Reproduction and verification attempts

- Initial ciphertext-only HTTP regressions reproduced two 429 outcomes instead of replacement success before the fix.
- Initial file poll matrix reproduced A retry, A late refusal, then an incorrect B success: 1 failing product case, 3 passing first-poll/pinned controls. The first guard still failed until the API adapter forwarded its explicit replay prohibition; both layers are now covered.
- Proven retained-reasoning bypass reproduced HTTP/SSE quota failures before projection activation and affinity re-derivation. Four initial test-body assertions needed canonical assistant content normalization; these were test setup corrections, not separate runtime defects.
- A stale unit expectation still required an account error penalty for reasoning rejection. It now asserts the new health-neutral contract while retaining the metric and non-retryable classification checks.
- Two guessed local `/codex/responses` POST paths were removed from the HTTP matrix after current routing showed they are unregistered. The four registered `/v1/responses` and `/backend-api/codex/responses` canonical/slash paths are tested; no alias or product change was introduced.
- The final existing `file_owner` bypass control caught overly broad activation. Independent resolved file ownership and single-account routing now disable prepared verified replay before admission; the control and all related selections pass.

Intermediate failed runs are not claimed green. The final disjoint selections below all passed. [test-results.json](test-results.json) stores result-only testcase identities without captured logs or temporary bootstrap tokens.

## Final focused tests

| Selection | PASS |
| --- | ---: |
| `test_replay_safety.py`, `test_auth_recovery_replay.py`, `test_failover_foundation.py`, `test_load_balancer_contract.py`, `test_select_with_stickiness.py` | 932 |
| New `tests/integration/test_routing_ownership_batch.py` and `tests/unit/test_routing_ownership_batch.py` | 79 |
| Existing files route/client/unary suites | 63 |
| Selected existing transient HTTP retry cases | 13 |
| Selected existing WebSocket model-rejection cases | 10 |
| Selected existing ownership, settlement, reasoning metric and retry controls | 47 |
| **Distinct total** | **1144** |

Zero skips, xfails or failing cases in these final selections. The Starlette/AnyIO deprecation warning remains non-blocking. Test databases are isolated SQLite; upstream adapters are controlled. This is focused local verification, not a full repository suite or live provider test.

Exact commands (all pytest commands also used `--tb=short --show-capture=no` and external `--junitxml` reports):

```powershell
uv run pytest tests/unit/test_replay_safety.py tests/unit/test_auth_recovery_replay.py tests/unit/test_failover_foundation.py tests/unit/test_load_balancer_contract.py tests/unit/test_select_with_stickiness.py -q
uv run pytest tests/integration/test_routing_ownership_batch.py tests/unit/test_routing_ownership_batch.py -q
uv run pytest tests/integration/test_routing_ownership_batch.py tests/unit/test_routing_ownership_batch.py tests/integration/test_proxy_files.py tests/unit/test_files_client.py tests/unit/test_unary_transport_failover.py -q
uv run pytest tests/integration/test_proxy_transient_retry.py -q -k 'model_not_found or model_entitlement or http_bypass or burst or request_error or safety_policy'
uv run pytest tests/integration/test_proxy_websocket_responses.py -q -k 'model_not_found or precreated_model_rejection'
uv run pytest tests/unit/test_proxy_utils.py -q -k 'stream_verified or reasoning_replay or keyed_empty_terminal or queued_penalty or transient_exhaustion or keeps_file_owner or post_refresh_owner_bound_burst'
uv run python scripts/check_proxy_architecture.py
uv run python scripts/check_cancellation_safety.py
uv run python scripts/check_proxy_timing_seams.py
uv run python scripts/check_settings_tiers.py
uv run python .github/scripts/check_simplicity_budgets.py
npx --yes @fission-ai/openspec@1.11.0 validate repair-five-routing-ownership-contracts --strict --no-interactive
npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict --no-interactive
git diff --check
```

Scoped Ruff, format and ty checks pass for the ten touched Python files: six runtime implementation/protocol files, the observability docstring, two new test files and the adjusted existing test file. Timing, cancellation, architecture, settings and simplicity guards pass. All 68 canonical specs and the strict delta validate. No settings, dependency, schema, dashboard, rendered docs or changelog change was introduced.

The current source was indexed without persisting a graph artifact. Initial discovery used the existing `codex-lb` graph; refresh returned `C-codex-lb`. Integration tests excluded by that index were inspected and executed directly.

## Requirement verification

Completeness: all 11 tasks; six added requirements / fifteen scenarios synchronized verbatim across the two owning capabilities. Correctness:

- File operation ownership: four new real-route poll cases and 63 file/client/unary controls.
- Ciphertext exception: four canonical/slash routes, status/frame, reasoning/compaction, keyed settlement-before-health, pinned/unresolved files, unknown extensions, ambiguity, burst, visibility and original/replacement rejection provenance.
- Proof-backed bypass reasoning: status/frame success, unchanged healthy owner, non-quota refusal, mismatched prefix, unknown reasoning, persisted quota selection and paused selection. Existing seven-history route boundaries and verified-owner unit cases remain green.
- Exact model scope and owner-safe rejection: real HTTP and WebSocket cases plus foundation classification controls.
- Rejection health: literal/recognized frames and HTTP 400, non-400 negative controls, metric preservation and unchanged envelopes.
- Hard continuity admission: active/paused/excluded/capped backoff combinations, pressure cleanup, unchanged counters and existing healthy-sibling/sticky/unbound cases.

Coherence: existing whole-request replay, typed transport, durable owner, settlement and lease cleanup mechanisms remain authoritative. The prepared quota projection never supersedes independent files or existing dispatch ownership. No actionable local finding remains in the selected scope. See [closure.json](closure.json) for exact saved registry and preservation checks.

## Limits

Live ciphertext acceptance, upstream policy/maintainer decisions, PostgreSQL/MySQL/multi-replica runtime, cloud checks, public artifacts and production are separate scopes. Prior partial findings and F-045/CI-04 remain unchanged. No commit, push, PR, merge, release or deployment was performed.

Final archive/readback: all 11 tasks complete; six requirements synchronized and preserved; own five rows closed locally,333 other source rows and129 unrelated baseline files unchanged. Queue338/146/7/185. Archive confirmed at 2026-10-09-repair-five-routing-ownership-contracts; HEAD unchanged. closure.json records final checks.
