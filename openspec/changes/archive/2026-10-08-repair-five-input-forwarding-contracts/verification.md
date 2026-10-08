# Verification: five input and forwarding contracts

Date: 2026-10-08, Europe/Kiev. Base local main: `8369ec720c5ac935f7a64fe3f30aa1cbc323f5e5`. Exactly five initially НЕ ПРОВЕРЕНО source records: **UP-PR-2488 / UP-PR-1952 / UP-PR-2277 / UP-PR-2099 / UP-ISSUE-2499**. The initial checkout already contained two verified local packages. Their 37 dirty/untracked files were backed up and hashed outside the repository before implementation. [Source snapshot](source-snapshot.json) records live metadata, heads and the five initial rows.

## Findings and resolution

| Record | Verified local result | Product-path evidence |
|---|---|---|
| [2488](https://github.com/Soju06/codex-lb/pull/2488) | Existing owner SSE framing independently verified | Entire owner-forwarding suite, including 30 client cases for LF/CRLF/CR/mixed separators, chunk sizes 1/7/65536, valid split UTF-8 and malformed-byte replacement; events arrive before EOF, with a separately parsed terminal. Existing deadline/scheduler, signing, cleanup-handoff and cancellation controls remain covered. |
| [1952](https://github.com/Soju06/codex-lb/pull/1952) | Fixed | Retain completed client tool-search call/output pairs and safe loaded function/custom declarations, optionally one namespace deep; reject hosted/MCP/server/failed/unknown shapes and nonboolean loading flags, including explicit null. HTTP/WS trim and fresh replay remove response-owned IDs without discarding full retained retry history. Durable relocation recognizes canonical query arguments and loaded tool identities. V1 compact raw-input validation rejects a trigger hidden behind a trailing instruction before normalization; existing terminal-trigger compatibility remains. Public HTTP/WS replacement-account and compact routes pass. |
| [2277](https://github.com/Soju06/codex-lb/pull/2277) | Existing stronger fork classifier independently verified | The fork classifies full resends through self-contained typed call/output pairs. Strings and singleton arrays remain deltas; parallel output-only arrays cannot discard their anchor. Four signed owner roundtrips and 16 real public route cases cover both canonical/slash families, 4095/4096-character strings, an 8192-character output and parallel function/custom outputs. The upstream size heuristic and new wire/capability negotiation were not transplanted; their classifier-disagreement problem is superseded by this conservative fork contract. Existing V2/body-omission/tamper controls remain. |
| [2099](https://github.com/Soju06/codex-lb/pull/2099) | Fixed | Track boolean async function/custom calls separately on HTTP bridge and direct WS; inject interrupted outputs only for synchronous calls, consume only exact typed delayed outputs, and clear pending state on owner/anchor changes. Validate settled async prefixes and reject client async relabeling against durable synchronous manifests. Relocation distinguishes async/sync identity and treats omitted/false as the same synchronous mode. Controlled HTTP/WS and real upstream WebSocket peer cases cover canonical/slash routes, intervening turns, delayed results, replay, malformed markers and ownership controls. |
| [2499](https://github.com/Soju06/codex-lb/issues/2499) | Existing catalog/source HTTP contract independently verified | Both Codex catalog views retain valid base instructions and multi-agent metadata, including persisted updates. All four Responses routes retain complete collaboration namespaces and forced/allowed tool choices while filtering unrelated unsupported tools. Missing/blank/malformed capability declarations remain conservative; explicit namespace opt-in still works. This verifies the local contract; a live real Codex parent/child session remains external. |

No source PR branch was merged. Reviewed focused upstream runtime/test hunks for 1952/2099 were adapted to this checkout; four context conflicts were resolved against current fork code, preserving its computer-output vocabulary, prewarm fields, response-size overrides and refresh-failover imports. The changed current source was re-indexed without a persisted graph artifact, and the new validators were found in the fresh `C-codex-lb` index. Integration paths excluded by that index were inspected directly.

## Red-before controls

```text
uv run pytest -q tests/unit/test_replay_safety_tool_search.py tests/unit/test_input_forwarding_contracts.py --tb=short --show-capture=no --timeout=30
```

Before production edits: **7 FAILED /26 PASS**. Five failures proved dropped/rejected valid tool-search history; two proved lost async continuity. Four signed delta roundtrips already passed, corroborating the fork's stronger existing classifier. After adaptation the initial extended unit selection passed 364 cases.

An independent loading-flag boundary test then reproduced an upstream-patch defect: explicit `defer_loading: null` was accepted (**1 FAILED /5 PASS**). The validator now checks presence and boolean type; all loading-flag controls pass in the final unit selection. Relocation coverage exposed the newly admitted item/marker identity gaps; the final comparison-key sweep and three direct relocation regressions pass.

The initial imported async integration run had **242 FAILED /380 PASS** because its unsafe-replay expectations used the upstream 502 envelope. The fork rejects these planning-stage continuations with exact **404 `bridge_previous_response_not_found`**. The tests now preserve that established envelope and still assert no alternate dispatch, while valid recovery, typed selector failures and policy-conflict controls retain their own contracts. The corrected entire async integration selection passes 448 cases. No production error classification was weakened.

## Final focused verification

The following disjoint selections total **1,980 passing Python tests**. Warnings are the existing Starlette BlockingPortal deprecation. The main unit selection deliberately deselects three independently reproduced baseline controls; this is a focused acceptance result, not a whole-repository green claim.

| Selection | Result |
|---|---|
| Replay safety, tool-search, independent input-forwarding, four async unit modules, source catalog/projection and fixture/sanitizer units, with the three baseline controls below deselected | **1257 PASS /3 deselected**, 6.83 s |
| Entire `tests/unit/test_http_bridge_forwarding.py` | **86 PASS**, 1.30 s |
| Existing HTTP bridge/proxy utility tests selected by tool_search, full_resend, interrupted and the two previous-response trim helpers | **67 PASS**, 3.06 s |
| Five new async integration modules, including controlled upstream sockets | **448 PASS**, 157.97 s |
| Source collaboration and persisted source catalog contracts | **97 PASS**, 24.31 s |
| New four-route delta-anchor boundary suite | **16 PASS**, 23.79 s |
| Existing/new HTTP/WS tool-search and raw compact-trigger route selection | **9 PASS**, 10.07 s |

Exact acceptance commands (omit `--junitxml` or choose an external temporary destination):

```text
uv run pytest -q tests/unit/test_replay_safety.py tests/unit/test_replay_safety_tool_search.py tests/unit/test_input_forwarding_contracts.py tests/unit/test_astra_async_tools.py tests/unit/test_astra_async_marker_validation.py tests/unit/test_astra_async_settled_prefix.py tests/unit/test_astra_async_durable_replay.py tests/unit/test_model_sources_catalog.py tests/unit/test_model_sources_projection.py tests/unit/test_codex_body_fixtures.py tests/unit/test_codex_body_sanitizer.py -k 'not the_committed_catalog_is_the_one_every_captured_fixture_records and not a_scratch_destination_needs_no_acknowledgement and not the_cli_reports_both_sides_of_the_scan' --tb=short --show-capture=no --timeout=45
uv run pytest -q tests/unit/test_http_bridge_forwarding.py --tb=short --show-capture=no --timeout=30
uv run pytest -q tests/unit/test_proxy_http_bridge.py tests/unit/test_proxy_utils.py -k 'tool_search or full_resend or interrupted or trim_websocket_previous or trim_http_bridge_previous' --tb=short --show-capture=no --timeout=45
uv run pytest -q -n 4 --dist worksteal tests/integration/test_astra_async_tools.py tests/integration/test_astra_async_marker_validation.py tests/integration/test_astra_async_settled_prefix.py tests/integration/test_astra_async_durable_replay.py tests/integration/test_astra_async_socket.py --tb=short --show-capture=no --timeout=45 --durations=5
uv run pytest -q -n 4 --dist worksteal tests/integration/test_model_source_collaboration.py tests/integration/test_source_catalog_contracts.py --tb=short --show-capture=no --timeout=45
uv run pytest -q tests/integration/test_bridge_delta_anchor_contracts.py --tb=short --show-capture=no --timeout=30
uv run pytest -q tests/integration/test_http_responses_bridge.py tests/integration/test_proxy_websocket_responses.py tests/integration/test_proxy_compact_triggers.py -k 'tool_search or raw_compact or trigger' --tb=short --show-capture=no --timeout=45
```

Four test workers use isolated databases. Work stealing distributes the 290-case async marker file across workers; loadfile had concentrated it on one worker. No production database was touched.

## Static and documentation verification

- Whole-repository `uv run ruff check .` and `uv run ruff format --check .`: PASS, 1498 formatted files.
- Scoped `uv run ty check` on all changed runtime modules, fixture sanitizer and new/changed contract test modules: PASS. Whole-repository typing retains six diagnostics in the preexisting dirty `test_background_jobs_runtime.py` and `test_load_balancer_multi_replica.py`; both files remain byte-identical to their initial backups.
- `scripts/check_proxy_architecture.py`, `check_cancellation_safety.py`, `check_proxy_timing_seams.py`, `check_settings_tiers.py`, `check_migration_topology.py`, and `.github/scripts/check_simplicity_budgets.py`: PASS. Settings stay 98/98, migrations stay 272 revisions with one intended head; no revision was added.
- `uv run mkdocs build --strict`: PASS. The existing traffic-parity page links to owning requirements and retains prior local documentation changes.
- CI-pinned `npx --yes @fission-ai/openspec@1.11.0 validate --type change --strict repair-five-input-forwarding-contracts` and `validate --specs --strict`: PASS, all **68/68** main specs. Three added requirements across Responses/tooling and one modified full-resend requirement are synchronized; existing scenarios are preserved.
- `git diff --check`: PASS.

## Independently reproduced inherited residuals

The wider neighboring suite is **not aggregate-green**. Before excluding inherited controls, replay/catalog/fixture selection reported 7 failures: four new shape/identity coverage gaps were repaired; three independent controls below remained. Expanded bridge/proxy selections reported **1950 PASS /1 FAIL** twice, and a narrower but still `async`-matching selection reported **1851 PASS /1 FAIL**. Pytest `-k async` also matches the `asyncio` marker; the final 67-case bridge selection uses actual subsystem keywords instead.

The baseline harness is saved at `C:/Users/ext/AppData/Local/Temp/codex-five-input-forwarding-20261008/baseline_controls.py`. It executes the original HEAD sanitizer and original HEAD Chat probe/wait functions in a separate test process, verifies the latter ASTs match this checkout, and reruns these exact four controls. **4/4 fail on original code**:

1. `test_the_committed_catalog_is_the_one_every_captured_fixture_records`: captured provenance expects `de111010ad347d62a87346760fb6746bc1a490483359b8cefd66e57daa0ed576`, while the committed catalog is `8127b8c46c8df716980afa7efed6d9ad6ac755ace20fd15d7bf5044df5d5baa2`.
2. `test_a_scratch_destination_needs_no_acknowledgement`: existing POSIX-style directory fsync raises PermissionError on Windows.
3. `test_the_cli_reports_both_sides_of_the_scan`: the same existing directory-fsync failure.
4. `test_chat_startup_probe_consumes_repeated_capacity_markers_before_first_event`: the unchanged Chat startup/wait functions time out under the test's 100 ms deadline, both in expanded selections and alone.

These residuals are outside the five selected source records. Fixture provenance was not falsified, persistence policy and Chat timing were not weakened, and six unrelated prior typing diagnostics were not silently repaired as extra tasks. Existing partials/F-045/CI-04 and external/provider/platform scopes remain.

## Completeness, correctness and coherence

- All five selected local contract scopes map to product-path tests and saved source evidence.
- Responses requirements map to replay validation, HTTP/WS state, trim/retry construction, synchronous manifest fencing and raw V1 compact validation. Fixture requirements map to the closed sanitizer item rules and scalar-marker/pairing tests.
- Existing ownership, reservation settlement, replay budget, prewarm, cancellation and signed-body contracts remain covered. No settings, dependencies, migrations or broad branch transplant were introduced.
- Controlled transport proofs do not certify live Codex parent/child sessions, provider persistence/acceptance, multi-replica PostgreSQL/MySQL runtime, public artifacts, new cloud gates, release or production deployment. No commit, push, PR, merge, release or deploy was performed.

Final per-row readback, queue counts and preservation results are recorded in [closure](closure.md).
