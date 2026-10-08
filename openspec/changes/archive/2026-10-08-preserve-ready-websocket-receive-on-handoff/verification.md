# Verification: ready receive remains owned during upstream handoff

Date: 2026-10-08, Europe/Kiev. Baseline: `e684963f7d6eafa86727447fc636e1726348c22a`, published fork main. [CI #82](https://github.com/Frozen811/codex-lb/actions/runs/37725985589) passed all integration shards (including the repaired incomplete-terminal race), browser smoke, DB suites, and the other jobs. Its matrix ended **33 successful /2 failed jobs**: the primary unit job and CI Required.

## Failure and deterministic reproduction

[Unit job](https://github.com/Frozen811/codex-lb/actions/runs/37725985589/job/113144294557) failed `test_proxy_responses_websocket_clean_close_handoff_retains_queued_turn`. The unchanged three-second bound expired with the relay polling its downstream receive task at `websocket/mixin.py:1775` instead of completing turn two. The ordinary test passed once in isolation, so the cloud failure was investigated rather than hidden by a rerun.

The relay recreates a receive task when it is `None` **or done**. A receive can become done during awaited upstream retirement between polling iterations; recreating it discards the second turn and begins waiting for a later client message. The fake client then waits for turn two to complete before disconnecting, so the discarded turn produces exactly the observed timeout.

The deterministic variant coordinates first close with the start of the second receive. Only parent-owned socket retirement releases that queued message and waits for it to become ready. Reader-owned closure is a different phase and would release too early. On the original code, the properly synchronized variant failed with the same three-second TimeoutError and same polling call site.

## Change and local validation

The relay now creates a receive task only when no task is owned (`None`). Its existing result-consumption finally clears ownership afterward. Explicit idle/drain cancellation, disconnect handling, transport retry, account ownership, and settlement remain unchanged.

| Scope | Result |
|---|---|
| `uv run pytest -q tests/unit/test_proxy_utils.py -k 'clean_close_handoff or downstream_disconnect or closes_idle_connection_during_drain or reject_response_create_observed_after_drain or rejects_response_create_observed_after_drain or delivers_active_terminal_before_drain_close or replays_staged_turn_before_drain_close or liveness_race or replay_cancellation or drain' --tb=short --show-capture=no` | 17 PASS |
| `uv run pytest -q tests/integration/test_proxy_websocket_responses.py --tb=short --show-capture=no` | 216 PASS |
| Scoped Ruff check /format and ty on source +edited unit file | PASS |
| Proxy architecture, cancellation safety, and timing seams | PASS |
| Strict OpenSpec 1.11.0 change and main specs | PASS, 68/68 capabilities |
| Requirement/delta comparison and whitespace | PASS |

These scopes are disjoint: **233 passing cases**, no skips/xfails. Both ordinary and queued-during-retirement schedules retain exactly two upstream connections, four lifecycle frames, and completed IDs `resp_turn_1` and `resp_turn_2`. The three-second scope timeout remains unchanged. Existing Starlette/AnyIO deprecation warnings remain.

## Completeness and publication boundary

One requirement/two scenarios and stable context are synchronized. The single ownership condition is bound by a controlled scheduling regression and existing disconnect/drain/replay/API coverage. All 338 source rows retain their existing statuses and text; no sixth source task is selected. The prior CI #82 failure remains historical and a new full successful run on the exact pushed repair SHA is required. Local checks do not establish cloud success, a release, production deployment, or hosted-provider acceptance.
