# Verification: HTTP phase provenance and abrupt drops

Date: 2026-10-04, Europe/Kiev. Clean starting source: `1edc716c5366d49ce95df00c57025871d237377c`, local `main` and freshly read `Frozen811/codex-lb:main`. Scope is exactly UP-ISSUE-2169, UP-ISSUE-2108, UP-ISSUE-2074. Registry status is local; a new commit needs its own GitHub CI run.

## Findings and implementation

- **2169:** the existing `_free_port()` returns only after its socket context closes. The native SSE fallback and compact fallback use the released loopback port, rather than retaining a bound non-listening socket. The real native helper reaches the selected endpoint exactly once; all four SSE outcomes and both compact outcomes preserve selected-owner trace, no Python fallback, no accepted-request replay and stream cleanup. No deadline increase, skip or native production change was necessary. Native macOS execution is not claimed.
- **2108:** six of twelve initial API provenance cases failed before the production fix. On all three routes, a keepalive/comment established first activity at 125 ms rather than the first upstream event at 250 ms; a local failure incorrectly established an upstream phase at 250 ms rather than null. Six zero/normalized-upstream-error controls passed. The HTTP consumer now excludes non-events, Codex keepalives and carriers marked `is_local`; it does not exclude a real upstream error merely because its response ID is local. Later parsed and verbatim forwarding remain lazy. No new schema, settings, metric labels or persistence barrier was added.
- **2074:** existing production behavior is confirmed through actual aiohttp WebSocket transport and all three HTTP routes. The fixture waits until real bridge processing has observed text or a buffered reasoning prelude before closing the socket. An abrupt transport abort returns one `stream_incomplete`, performs no second connection/send, no `record_error`, and no eventless-window signal. Authored 1011 closes and invalid binary messages return one failure with one real health penalty and no replay. The contradictory older eventless-only requirement was removed; its later replacement remains authoritative.

## Executed checks

| Command / selection | Result |
|---|---|
| `uv run pytest -q tests/integration/test_usage_generation_contracts.py -k http_phase_provenance --tb=no --show-capture=no` before production fix | **6 failed, 6 passed**, 44 deselected; failures at real persisted-row assertions |
| Same initial 12-case selection after production fix | **12 passed** |
| `uv run pytest -q tests/integration/test_usage_generation_contracts.py tests/integration/test_bridge_contract_wire.py tests/unit/test_response_timing.py tests/unit/test_http_stream_latency_cohort_samples.py --tb=short --show-capture=no` | **132 passed**, 106.80 s; includes real loopback upstream wire/usage/phase-zero checks and verbatim relay assertions |
| Final `test_usage_generation_contracts.py -k http_phase_provenance` after adding later local-created and optional-metrics coverage | **30 passed**, 24.89 s; no skips. Actual installed Prometheus counts/sums and four stable label names checked; disabled metrics preserve all DB/API assertions. Optional metrics remain optional in CI. |
| Final `test_bridge_contract_wire.py -k post_output` including eventless-signal assertions | **18 passed**, 33.46 s; no skips |
| `cargo build --locked -p codex-lb-egress-worker --bin codex-lb-native-egress` | PASS; freshly checked debug helper |
| `CODEX_LB_NATIVE_EGRESS_TEST_BINARY=C:/codex-lb/target/debug/codex-lb-native-egress.exe uv run pytest -q tests/integration/test_native_sse_egress.py -k 'routed_native_selection_stops_after_response_head or native_compact_routed_fallback_keeps_metadata_and_never_replays_accepted_post' --tb=short --show-capture=no` | **6 passed**, 6.91 s; no skips |
| Timing/cohort and bridge/utils selector for `response_timing`, `latency_cohort`, account neutrality, post-output and protocol controls | **38 passed**, 2538 deselected, 6.25 s |
| `uv run ruff check .`; `uv run ruff format --check .`; `uv run ty check --output-format concise` | PASS; complete configured tree, 1458 formatted files |
| `check_proxy_architecture.py`, `check_cancellation_safety.py`, `check_proxy_timing_seams.py`, `check_settings_tiers.py`, `check_migration_topology.py` | PASS; no ratchet weakening or migration changes |
| `uv run python .github/scripts/check_simplicity_budgets.py` | PASS; root 0/0, nav 5/5, no new settings or README section |
| CI-pinned OpenSpec 1.11.0 strict change and strict main-spec validation | PASS; **68/68** main specs |
| `git diff --check` | PASS |

The harmless pytest warning is Starlette's deprecated BlockingPortal alias. The first immediate-abort fixture raced unread socket bytes and was replaced by explicit progress synchronization before assessing post-output behavior; those fixture failures are not recorded as a production defect. The final signal assertion was rerun after the larger selection. Test counts overlap and are not summed as unique coverage.

## Completeness, correctness and coherence

All six change tasks are complete. The HTTP provenance requirement's three scenarios are covered by real HTTP API, persisted request rows, real exporter observations, explicit absence and zero controls, and existing real loopback upstream tests. The obsolete bridge requirement is removed and the retained contract is covered by real transport plus authored-close/protocol negative controls. Native portability is established by the corrected socket lifetime and real helper execution on Windows; actual native macOS remains external platform scope. The changes preserve existing routing, settlement, ownership, replay and output-forwarding contracts. No critical or warning issue remains in this bounded local implementation.

## Publication and cloud boundary

This report proves source/local Windows behavior. New commit/push status and exact-head GitHub CI are separate; no new-head cloud success is claimed here. Live hosted-provider traffic, production rollout, native macOS, historical minute-long stalls, F-045/CI-04 stability and release/public artifacts remain outside the three selected local closures. User approval of the pending push question is required by the repository git workflow before sending the new commit to fork main.
