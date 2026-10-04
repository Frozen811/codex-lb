# Verification: bridge refusal, model transition and terminal settlement

Date: 2026-10-04, Europe/Kiev. Base SHA: `94c9a8c24cc0dfdd4c5bce00aa1c46e6bc9d9b6d`. Initial worktree was clean. Exactly UP-ISSUE-2389, UP-ISSUE-2388 and UP-ISSUE-2033 are selected; no other source-queue row is closed by this batch.

## Product evidence

| Registry item | Result and evidence |
|---|---|
| UP-ISSUE-2389 | Existing fix verified. Real LoadBalancer selection returns continuity_owner_conflict after a real SQLite sticky mapping disagrees with the required durable owner. Recovery selects the other allowed account and durably registers the same turn token. The next turn, including reasoning output, resolves to that child without another conflict or connection. Three ingress variants pass. Three missing-table claim refusals and three recovered-child renewal refusals also pass. Existing protected-alias, reversible rollback, cancellation and one-fork controls retained. |
| UP-ISSUE-2388 / F-074 | Fixed 14 pre-dispatch producer branches. See [refusal-audit.md](refusal-audit.md) for all 27 candidate contexts and why seven mixed/post-dispatch contexts retain transport provenance. Forty submit/startup cases cover canonical/slash/native/internal ingress and native delivery after commitment. Sixteen creation cases cover compatibility, admission handoff, owner metadata and ring lookup. Other durable producers are reached by six model-transition failure cases. Signed internal responses carry the provenance header; public responses retain status/code or one terminal plus DONE. No new upstream frame is sent; real reservations and leases are cleaned up. Five request-state controls retain transport provenance after prior send/events/replay. |
| UP-ISSUE-2033 / F-075 | Existing single-terminal exception containment verified; an additional ordering defect fixed. An unanchored keyed later-event/raised-error path could call health while its reservation remained reserved. Settlement now waits whenever account-error health is pending. Eighteen route cases cover first-event/later-event/raised failures, anchored and unanchored keys, and all three ingress variants. Health callback reads the actual SQLite reservations in terminal state, then raises; exactly one original terminal is delivered and the exception is logged once. |

Compatibility/admission callbacks, missing-table/CAS/metadata failures and lease interleavings are deliberate fault injection. Dispatch, loopback WebSockets, real balancer selection, database aliases, reservation settlement and public route normalization remain real. Post-commit cases inject a progress event at the bridge boundary to establish commitment before invoking the actual refusal producer; they do not claim that native clients ordinarily receive injected heartbeats.

## Negative control

See [baseline.md](baseline.md). Retaining the new tests and replacing the six changed runtime files with HEAD bytes gives **24 failed, 6 passed, 53 deselected** in 35.56 seconds. All runtime bytes were restored in finally and verified byte-identical to their saved state.

The current baseline reproduces misclassification through native transport shaping and loss/replacement of the intended refusal, plus two health-before-settlement failures. It does not establish that every current producer literally returns a zero-byte body; that was the original upstream report. The final assertions establish preserved local status/code and exactly one actionable terminal after commitment. Model convergence and pre-existing exception containment already worked and were independently verified rather than claimed as new runtime fixes.

## Commands and results

- `uv run pytest -q tests/unit/test_bridge_refusal_provenance.py tests/integration/test_bridge_refusal_transition_terminal.py --tb=short --show-capture=no --disable-warnings` — **88 passed**, 1 warning, 125.81 s; no skips/failures.
- `uv run pytest -q tests/unit/test_proxy_http_bridge.py tests/unit/test_proxy_utils.py tests/unit/test_http_bridge_forwarding.py -k 'model_transition or recovery_submit or protected_alias or active_recovery_alias or route_health_failure_keeps_one_terminal or preserves_health_after_disconnect or native_codex_previsible_transport_failure_is_never_replayed or local_refusal or owner_forward_non_200_carries_local_refusal_provenance or cooldown_suppression or submit_suppresses_hard_key or submit_rejects_a_denied_proxy_anchor' --tb=short --show-capture=no --disable-warnings` — **36 passed**, 2593 deselected, 1 warning, 2.73 s.
- `uv run pytest -q tests/unit/test_proxy_utils.py -k 'stream_with_retry and (keyed or cancel or settlement or terminal)' --tb=short --show-capture=no --disable-warnings` — **25 passed**, 1435 deselected, 1 warning, 3.99 s.
- Scoped `uv run ruff check` and `uv run ruff format --check` on the six changed runtime files and two new test files — PASS, eight files formatted.
- Scoped `uv run ty check` on the six changed runtime files — PASS.
- `uv run python scripts/check_proxy_architecture.py`, `scripts/check_cancellation_safety.py`, `scripts/check_proxy_timing_seams.py`, `scripts/check_settings_tiers.py`, and `.github/scripts/check_simplicity_budgets.py` — all PASS; settings 98/98, no budget increase.
- `npx --yes @fission-ai/openspec@1.11.0 validate repair-bridge-refusal-transition-terminal --strict` — PASS.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict` — **68/68 PASS**.
- `git diff --check` — PASS.

Counts are focused selections, not a full repository suite. Earlier setup errors from incorrect test seam names were corrected before the baseline control and final run; they are not represented as product regressions or green evidence.

## Requirement mapping and review

- Local-refusal scenarios map to `test_native_local_refusal_is_delivered_before_dispatch`, `test_creation_refusal_sites_preserve_native_error`, the two model-transition persistence failure cases and `test_local_refusal_proof_excludes_previously_dispatched_states`. Existing native transport failure and signed forwarding regression tests retain negative controls.
- Successor continuity maps to `test_model_transition_successor_converges_on_the_next_turn` with no storage failure; real owner conflict and the same token on the next turn are asserted. Existing protected recovery alias and recovery_submit tests cover rejection, rollback, cancellation and queue admission.
- Post-terminal health scenarios map to `test_health_failure_after_real_settlement_preserves_one_terminal` and the existing route-health/disconnect tests. The callback verifies committed reservation state before injecting its ordinary failure.
- Fresh source review checked that each added marker precedes current-request enqueue/send, replay permission remains separately guarded, and the health barrier does not add blocking settlement for ordinary successes. No change to settings, schema, migration, transport replay eligibility or account ownership selection is introduced.

The three normative blocks are synchronized verbatim to the owning main spec. Stable purpose, rationale, examples and limitations are in its context.md. Registry closure and task completion are checked before archive.

## Limits

Local ASGI/loopback/SQLite evidence only. Live Codex clients/providers, PostgreSQL/MySQL runtime, multi-process races, exact-head cloud CI/review, public artifacts and production are not certified. Existing partial tasks, F-045 and CI-04 retain their statuses. No commit, push, release or deployment was performed.

Final registry readback confirms the three selected rows have explicit local closure and verification links; the source queue has 54 local closures, seven partial and 236 unchecked rows. Exactly those three pre-existing source rows changed. All six tasks are complete; all eight code/test hashes match the verified bytes.

## Subsequent local commit request

On 2026-10-04 the user explicitly requested a commit in main. The checkout is already on main at the recorded base SHA, and the fork remote identifies Frozen811/codex-lb. Before staging, all eight runtime/test fingerprints and the completed task list were reread and matched. The test results above describe the preceding implementation stage; the containing Git commit records the subsequent local source snapshot. No push, release or deployment is authorized by this commit request.
