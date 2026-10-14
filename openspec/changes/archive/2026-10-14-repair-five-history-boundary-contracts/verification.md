# Five history and recovery contracts - local verification, 2026-10-14

Initial HEAD: cfc939cc69e6534996365a348b74eaf414283f34, branch main. Exactly five initially unverified rows are owned: UP-ISSUE-2269, UP-ISSUE-1942, UP-ISSUE-568, UP-ISSUE-986 and UP-ISSUE-1924. Existing dirty work was retained. No commit, push, PR, merge, release, production migration or deployment was performed.

## Completeness, correctness and coherence

| Dimension | Evidence |
|---|---|
| Completeness | Exactly five source rows receive saved status and verification links; the summary is synchronized. Tasks, delta specs and stable context are present. |
| Correctness | Occurrence-aware classification and optional timing have regression coverage; existing eventless, slimming and quota behavior is independently verified at product routes. |
| Coherence | Immediate timing remains the compatible default; hard ownership, existing failure recovery, account exclusion, API-key settlement and artifact-preserving slimming remain authoritative. |

| Row | Outcome |
|---|---|
| UP-ISSUE-2269 | Fixed classification of a second output reusing an already consumed call. Four tool protocols, complete repeated pairs, cross-protocol refusal and normalized/forwarded strings at4080/4095/4096/4097/8192 characters are covered. All four HTTP canonical/slash routes preserve explicit continuation anchors and output order. Existing signed legacy/v2 forwarding and remote-owner anchor controls pass. |
| UP-ISSUE-1942 | Existing bounded eventless termination and safe recovery verified without a further runtime edit. Four real HTTP aliases terminate within the five-second test bound with a structured error or terminal response.failed, rather than keepalive-only SSE. Empty-upstream/pinned controls, pre-created-close recovery and cooldown retirement/active-probe/admission-waiter ownership tests pass. |
| UP-ISSUE-568 | Existing item-preserving slimming verified without a further runtime edit. File references, tool IDs, item count, historical assistant content, latest suffix and prompt-cache identity survive all four HTTP aliases. Existing HTTP/native WebSocket slimming and local400 payload_too_large guards pass. The broad oldest-item omission design remains reverted; the maintainer closed its upstream tracker as obsolete. |
| UP-ISSUE-986 | Added the persisted settings API option stickyReallocationTiming=after_compaction. At96-percent owner pressure an ordinary turn retains account A; explicit compact can select account B at10 percent. Four HTTP aliases, both native WebSocket routes and real previous-response hard-owner compaction are covered. Default immediate policy, strict writes, omission preservation and database defaults are verified. No new environment field or dashboard UI control. |
| UP-ISSUE-1924 | Existing narrowed quota-rejection exception independently verified without a further runtime edit. Twenty-four metered HTTP cases cover status429 and first-event failures, four aliases, plain images, retained reasoning and compaction. The entire normalized input and ciphertext remain unchanged on the replacement, and exactly one reservation is finalized. Visible-output, pinned, burst and owner controls pass. This covers the maintainer's retained-state clarification, rather than repeating the rejected plain-image affinity diagnosis. |

## Regression and final test evidence

The final regression harness, run temporarily against the three saved initial source files, reproduced **9 failures /9 passes**: four repeated-output cases, the deferred sticky-thread selection case and four public HTTP timing paths. Current source bytes were restored in finally and checked byte-identical. Earlier harness failures from missing instructions, normalization expectations, reservation status, historical seed defaults and nested test-client shutdown were corrected to existing contracts; they are not counted as product defects.

**534 distinct tests passed; zero failures, skips or xfails in the final selections.** Two additional backend executions passed the migration contract on PostgreSQL and MySQL. JUnit identities were audited for duplicate coverage across these selections:

1. `uv run pytest -q tests/unit/test_history_boundary_contracts.py tests/integration/test_history_boundary_contracts.py --tb=short --maxfail=2`: **71 passed**,66.95s. Includes all new routes, optional timing, hard owner, quota/ciphertext, settings validation and SQLite migration cases.
2. `uv run pytest -q tests/unit/test_select_with_stickiness.py tests/unit/test_proxy_utils.py -k 'stickiness or sticky_key_for or slim_response_create or connect_proxy_websocket' --tb=short --maxfail=3`: **117 passed**,1418 deselected,13.30s.
3. `uv run pytest -q tests/unit/test_proxy_utils.py -k 'stream_with_retry or stream_responses_websocket' --tb=short --maxfail=3`: **99 passed**,1381 deselected,3.09s.
4. `uv run pytest -q tests/integration/test_settings_api.py tests/unit/test_http_bridge_forwarding.py tests/unit/test_proxy_http_bridge.py -k 'settings_api or forwarding or payload_looks_like_full_resend or cooldown_suppression' --tb=short --maxfail=3`: **190 passed**,1090 deselected,78.05s.
5. `uv run pytest -q tests/integration/test_proxy_transient_retry.py -k '429 or after_text or pinned_previsible or empty_upstream or 401 or auth_recovery_preserves' --tb=short --maxfail=3`: **36 passed**,99 deselected,35.78s.
6. `uv run pytest -q tests/integration/test_proxy_compact.py -k 'pinned or owner or settlement or preflight or budget or deadline' --tb=short --maxfail=3`: **15 passed**,42 deselected,15.38s.
7. Existing HTTP bridge nodes `test_v1_responses_http_bridge_rejects_oversized_response_create_before_upstream`, `test_v1_responses_http_bridge_slims_historical_inline_artifacts_and_succeeds`, `test_v1_responses_http_bridge_retries_once_when_upstream_closes_before_response_created` and `test_v1_responses_forwards_hard_continuation_with_canonical_prompt_cache_key`: **4 passed**,4.54s.
8. Existing native WebSocket nodes `test_backend_responses_websocket_rejects_oversized_response_create_before_upstream` and `test_backend_responses_websocket_slims_historical_inline_artifacts_and_succeeds`: **2 passed**,2.44s.

The existing Starlette/AnyIO BlockingPortal deprecation and test SQLite lifetime-lock teardown warning remain documented. Test storage is provisioned through tests/runtime.py before engine imports. Provider transport is faked; application routes, account selection, settings, reservations and SQLite persistence are real. Native WS tests use the off-loop client and an actual metered key; compact runs before nested lifespan shutdown.

## Migration and static evidence

- Revision20261014_000000_add_sticky_reallocation_timing extends20261010_000000_add_source_catalog_discovery with a non-null VARCHAR(32) and immediate server default. Existing historical rows keep the compatible mode; downgrade removes only the new preference, and re-upgrade initializes immediate again.
- The migration test upgrades the entire current fork lineage to the parent, uses its seeded settings row, upgrades head, verifies the default and schema drift, downgrades the new revision and re-upgrades. Disposable SQLite passed; the same targeted test passed with TIMING_MIGRATION_TEST_URL on **PostgreSQL16.15** and **MySQL8.4.11**. Those two locally created containers were identity-checked and removed. No production/application database was substituted.
- `git fetch fork main` completed. Migration topology passes with276 revisions and one intended head. The checker uses its existing origin/main base reference. Static duration safety passes; this is not a production migration-duration benchmark.
- Repository Ruff and format checks pass on1564 files. Scoped ty passes for changed model/settings/routing/support/transport application paths.
- Proxy architecture, cancellation safety, timing seams, settings tiers and simplicity budgets pass. Settings fields remain98/98; no env surface is added. README218/225, headings10/10, env54/60, nav5/5 and root extras0/0 remain within budgets.
- Strict delta validation and canonical strict OpenSpec68/68 pass. Both added requirements and stable context are synchronized. The timing requirement explicitly gates generic pressure scenarios, preserving default behavior.
- Full batch source diff and new files reviewed; git diff --check passes. Git's existing LF-to-CRLF advisory messages are not whitespace errors.
- The fast graph refresh still omitted the new affinity helper. Final impact review used current source/Serena, targeted regression suites and static checks; graph completeness is not claimed.

## Registry and preservation

The five selected own rows are marked closed locally, reread and linked here. All354 unselected source rows remain byte-identical. All62 unrelated pre-existing dirty files are byte-identical by SHA256; shared file changes and the batch scaffold are explicitly excluded from that count. Previous dirty changes in shared runtime files and the original spec/context content are retained. closure.json records the row readback, hashes and current queue arithmetic.

Exact JUnit reports, static-results.json, initial source copies, red-final.log, batch source diff and the duplicate audit are at C:/Users/ext/.codex/visualizations/2026/10/14/01a138d7-c46a-7260-8dce-0c32aef75233/five-history-boundaries/.

## Practical limits

Local evidence covers Windows/Python, real disposable SQLite/PostgreSQL/MySQL, synthetic provider transports and supported HTTP/native WebSocket ingress. A deployed relay/nginx chain, live provider/Desktop behavior, prompt-cache billing, distributed rolling upgrades and hosted current-head CI are not established. The optional timing preference is exposed through settings API; a new visual dashboard control is not part of this batch. Existing partial registry scopes and F-045/CI-04 retain their prior status.
