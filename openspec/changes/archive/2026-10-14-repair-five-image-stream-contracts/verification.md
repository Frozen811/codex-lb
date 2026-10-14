# Verification: five Images and streaming registry contracts

Date: 2026-10-14, Europe/Kiev. Initial HEAD: cfc939cc69e6534996365a348b74eaf414283f34, main. Exactly five selected rows were initially НЕ ПРОВЕРЕНО: UP-ISSUE-2304, UP-ISSUE-620, UP-ISSUE-1950, UP-ISSUE-1711 and UP-PR-2520.

## Results by source row

| Row | Independently verified local result |
| --- | --- |
| UP-ISSUE-2304 | Existing Flare/Sunburst model support verified through generation and edit aliases, real account routing, model validation, tool configuration, edit input bytes, public model observations and metered SQLite settlement. Public edits use multipart and native Codex edits use JSON. Removed the contradictory duplicate Luna host requirement; canonical Sol/Astra/5.5 behavior remains unchanged. |
| UP-ISSUE-620 | Fixed completed image results being replaced by a trailing response.incomplete. Product tests cover both models, four generation/edit paths, n=1/2, output/usage aggregation, one public reservation and one bounded route observation. Existing fan-out tests independently cover partial failure, all-failed, unexpected exceptions, log-rewrite failure and repeated cancellation during cleanup/settlement/release. The existing 1..10 admission limit and streaming n>1 rejection remain verified. |
| UP-ISSUE-1950 | Existing hosted computer screenshot slimming independently verified through all four HTTP response aliases and both native WebSocket routes with a reduced serialized-payload budget. Historical screenshot bytes are replaced; call IDs, call items, current turn and original input remain intact. All four explicit compact aliases preserve screenshot input and return the encrypted checkpoint. Existing unit tests cover hosted screenshot transport and protected recent suffix/oversize refusal. |
| UP-ISSUE-1711 | Existing authentic owner terminal handling independently verified on both native WebSocket routes: completed root, anchored follow-up, visible output, exact rate_limit_exceeded message/type, one failing request log, one connection, no replay and upstream closure without cleanup-budget warning. Lifecycle tests cover terminal ownership, cancellation, separate scope/drain budgets, repeated cancellation and failure-safe finalization. Historical deployment interruption ratios are not reproduced or asserted. |
| UP-PR-2520 | Existing extraction independently verified: ProxyService.stream_responses binds the extracted helper, preserves lazy retry iteration, payload identity, filtered headers, logging, defaults and explicit options. Real image/HTTP/WebSocket routes exercise the binding; existing startup-error and TTFT suites cover lazy response entry and retry ownership. No additional timing or model-source behavior was introduced. |

## Regression evidence

Before the runtime change, a valid unit regression failed on completion followed by incomplete. After correcting initial harness assumptions about multipart input and provider-start ordering, three public generation/edit route regressions returned 502 instead of the expected completed image. These are the product reds; the initial edit-shape and ordering failures are harness mistakes.

The runtime fix places the completed-result guard at the top of the collector's drain loop, replacing separate late-error guards. No exception swallowing, immediate return, new retry, setting or schema is added. Original completed output and tool usage stay authoritative while iterator finalization still runs.

The full new test harness initially assumed every fan-out child must dispatch upstream even when the shared account becomes unavailable during admission. A selection_state_changed refusal is valid and counts as a failed subcall. The final negative assertion permits that precise refusal only for n>1 all-failed cases and still requires zero successful usage, one released reservation, cleanup of every started provider call and one observation. n=1 requires the original image_generation_failed; successful fan-out still requires all n provider calls and images. No routing behavior was changed for this harness issue.

## Final checks

**432 distinct tests passed, zero failures/skips/xfails in the final selections.** JUnit identities were checked across all three reports: 432 executions, no duplicates.

1. `uv run pytest -q tests/unit/test_image_stream_contracts.py tests/integration/test_image_stream_contracts.py tests/unit/test_ttft_optimization.py --tb=short --maxfail=3`: **93 passed**, 63.73s. Includes all 66 new unit/product cases and 27 existing TTFT cases.
2. `uv run pytest -q tests/unit/test_images_schemas.py tests/unit/test_images_translation.py tests/unit/test_images_fanout.py tests/integration/test_image_fanout_settlement.py tests/integration/test_proxy_images.py --tb=short --maxfail=3`: **277 passed**, 165.23s.
3. `uv run pytest -q tests/unit/test_websocket_terminal_cancellation.py tests/unit/test_proxy_utils.py -k 'websocket_terminal_cancellation or slim_response_create or stream_responses_websocket_slims_hosted or stream_responses_returns_before_first_upstream_event or stream_responses_streams_post_startup_proxy_error or filter_inbound_headers' --tb=short --maxfail=3`: **62 passed**, 1452 deselected, 7.90s.

The initial 60-case run and the separate 6 added compact/mid-turn cases are superseded by selection 1 and not counted again. The earlier 92-pass/1-failure aggregate runs exposed the harness's invalid all-children-dispatch assumption; they are retained as historical failures, not reported as green.

Completeness: 7/7 tasks after registry readback; one added requirement and one removed duplicate are synchronized. Correctness: both completion-precedence scenarios map to the collector guard and public routes; removal maps to the existing compatible-host requirement. Coherence: existing adapter/routing/settlement boundaries are retained. No critical or unaddressed local verification findings remain.

Static checks: repository Ruff and format (1566 files), scoped ty for images_service.py, proxy architecture, cancellation safety, timing seams, settings tiers, migration topology (276 revisions, one existing head), static migration safety and simplicity budgets passed. No migration is added. Strict delta validation and all 68 canonical specs passed. The first static-results wrapper hit Windows cp1251 while printing a success glyph after the checks; a UTF-8 wrapper repeated the checks successfully and saved each exit code incrementally.

## Scope and preservation

All 89 unrelated initial dirty files are byte-identical by SHA256. The previous Images spec/context content is reconstructable byte-for-byte by removing only this batch's additions and restoring the removed duplicate requirement. Exactly five own source rows are updated and reread; other 354 source rows remain byte-identical. See closure.json for hashes, saved row readback and queue arithmetic.

The source/test/spec diff was reviewed against the initial snapshot. Discovery used a refreshed graph followed by current-source/Serena reads and focused traces; dynamic method binding and integration-test graph gaps were checked directly. The graph is navigation evidence, not runtime proof.

## Practical limits

Local evidence covers Windows/Python, disposable SQLite, real application HTTP/WebSocket ingress and synthetic upstream transports. The existing Starlette/AnyIO BlockingPortal deprecation and SQLite test lifetime-lock teardown warning remain; no skipped backend is counted as a pass. Live provider/Desktop behavior, historical production failure rates, cloud CI, distributed deployments and published artifacts are not verified. Prior partial rows, F-045 and CI-04 remain unchanged. Commit, push, PR, merge, release and deployment were not performed.

Raw logs, JUnit reports, static-results.json and preservation snapshots: C:/Users/ext/.codex/visualizations/2026/10/14/01a139bf-5041-7f51-8e0a-fa72b879f98e/five-image-stream-contracts/.
