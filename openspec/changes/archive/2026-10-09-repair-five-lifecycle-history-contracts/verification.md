# Verification: five lifecycle and history records

Date: 2026-10-09, Europe/Kiev. Base local main: `005c8aa4d06be1d0d2f1ccdb2e0f90b725884f8e`.

Exactly five initial unverified records: **UP-PR-2506, UP-PR-2255, UP-PR-2344, UP-PR-2133, UP-PR-2484**. Initial rows, live GitHub state/head metadata and prior dirty hashes are in [source-snapshot.json](source-snapshot.json). GitHub author test counts and deployment statements are not local evidence.

## Reproduction and fixes

| Record | Independent finding and resulting behavior | Regression evidence |
|---|---|---|
| UP-PR-2506 | Cancelling the stop caller during fallback cleanup left the worker absent from the clean-shutdown ownership proof. Track fallback cancellation before waiting, until worker completion. Cooperative grace still propagates caller cancellation without cancelling the worker. | New unit interrupted-stop failure before the fix; existing stop/budget tests and a real held SQLite poller read pass. |
| UP-PR-2255 | Existing v1/backend-api upgrade denial already returned retryable HTTP 503, but canonical `/codex/responses` and its slash variant returned a generic detail body. They now retain the same OpenAI `proxy_unavailable` envelope and Retry-After 5. | Two real WebSocket canonical route failures before the fix; eight route controls cover canonical/equivalent/slash/non-proxy/lookalike paths. No rejected route increases in-flight ownership. |
| UP-PR-2344 | A done settlement still awaiting its ownership callback was filtered out, exposing false zero. Missing/malformed observations had no unknown state. Registered owners now survive callback transfer; a strict typed snapshot derives pending/drained, and unavailable/inconsistent observation returns unknown without a count. | Callback-transfer unit failed before the fix; six initial real status-route negative cases failed. Expanded route controls cover strict integer/boolean validation, actual detached service ownership and pending-to-drained completion. |
| UP-PR-2133 | Lifespan heartbeat awaited optional reconciliation/sweeping/cap refresh in serial. A held reconciliation prevented subsequent real SQLite ring heartbeats. Four independent fixed-count phase owners now await their own passes, retry ordinary failures, wake on shutdown, and drain before bridge teardown. Ring operations use background session admission by default; explicit factories retain compatibility. | Corrected real lifespan barrier failed waiting for subsequent heartbeats before the fix; the final test proves repeated heartbeats and other phases while reconciliation remains single-flight, including a first-pass failure/retry. A real lifespan with cancellation-deferring maintenance withholds CLEAN. Ring fingerprint/readiness and telemetry lifecycle controls pass. |
| UP-PR-2484 | Existing capped SQL implementation independently satisfies bounded per-account reads. Its normative spec still allowed SQLite to ignore the cap; align that contract with the verified implementation and preserve the genuinely uncapped cache path. No usage query rewrite was necessary. | Twelve added repository cases cover primary/null and secondary windows, caps 0/1/3, timestamp ties, exact recent-floor inclusion and duplicate-free ordering. Existing SQLite index-plan and dashboard projection/overview controls pass. |

[Initial boundary failures](red-before.log) contain 2 substantive unit and 8 route failures; their initial heartbeat setup lacked an initialized proxy service and is superseded by the separately corrected [real lifecycle reproduction](red-heartbeat.log). Early test-harness mistakes were corrected before product conclusions. The optional upstream PR readiness-envelope redesign is not transplanted: this record verifies its heartbeat-isolation concern under the fork's existing readiness contract.

## Exact final commands

```powershell
uv run pytest tests/unit/test_scheduler_task_shutdown.py tests/unit/test_graceful_shutdown.py tests/unit/test_shutdown_drain_bounds.py tests/unit/test_health_probes.py tests/unit/test_ring_membership.py tests/unit/test_dashboard_projection_history_cap.py tests/unit/test_lifecycle_history_batch.py tests/integration/test_lifecycle_history_batch.py tests/integration/test_health_probes.py tests/integration/test_internal_drain_provenance.py tests/integration/test_usage_repository.py tests/integration/test_dashboard_overview.py tests/integration/test_cache_invalidation_bus.py -q --tb=short
# 273 passed, 10 skipped, 13 warnings (81.69s).

uv run pytest tests/unit/test_proxy_http_bridge.py::test_heartbeat_maintenance_runs_all_bridge_passes tests/unit/test_proxy_http_bridge.py::test_heartbeat_maintenance_isolates_a_failing_pass tests/unit/test_proxy_http_bridge.py::test_heartbeat_maintenance_tolerates_a_missing_service_or_pass tests/unit/test_otel.py tests/integration/test_shutdown_drains_database_tasks.py tests/integration/test_graceful_websocket_process_shutdown.py -q --tb=short
# 53 passed, 8 skipped, 1 warning (2.19s).
```

The telemetry follow-up initially exposed eight stale test factories requiring a positional session factory. All six factories now accept the service's optional factory contract; their original assertions remain intact. The isolated telemetry module then passed 50/50. Focused suites are not a full-repository or cloud-CI claim.

Scoped Ruff lint/format and ty cover all modified app files and tests; proxy architecture, cancellation safety, injected timing, settings-tier and simplicity budget gates pass. Strict change validation passes. All 68 canonical specs pass strict validation before sync; final synced/archive validation is recorded in the closure evidence.

Codebase-memory was checked, then refreshed in fast mode after the lifecycle changes (62938 nodes, 272210 edges, persistence disabled). The new maintenance phase resolves to its actual current source and main caller. Integration tests are excluded from the index and were mapped directly. Graph name-based edges are navigation evidence, not runtime proof.

## Scenario and design verification

- Persistence callback-transfer, missing/throwing/invalid observation and fully-drained scenarios map to the new unit and public internal-route tests.
- Interrupted fallback and cooperative grace map to new interrupted-stop coverage and existing scheduler stop tests, plus the held real SQLite poller transaction.
- Canonical WebSocket denial maps to real upgrade controls, preserving generic non-proxy denial.
- Optional maintenance isolation, single-flight, partial failure/retry and shutdown map to actual lifespan tests. Clean-shutdown refusal remains owned until delayed cleanup finishes.
- Capped SQLite history, ties, floor-inclusive rows and zero cap map to twelve added repository cases and existing query-plan/dashboard controls. Existing PostgreSQL requirements/scenarios remain in the delta.

No missing implementation requirement, unexplained scenario gap or design contradiction remains in the local selected scope. Normative deltas retain old scenarios; stable purpose/rationale/failure examples are promoted into canonical context.

## Limits

The main suite has 9 PostgreSQL-only skips and 1 Windows `tzset` skip. Follow-up process controls require POSIX signals and remain skipped on Windows. Reflection/deprecation warnings are reported, not failures. File-backed SQLite and in-process lifecycle evidence do not certify live PostgreSQL/MySQL, SQLite lock isolation across replicas, POSIX SIGTERM, native Windows process termination, provider clients, public artifacts, cloud CI or production. Background-pool separation isolates connection admission, not SQLite's writer lock. Previous partial/F-045/CI-04 and public/platform residuals remain untouched. No commit, push, PR, merge, release or deployment is authorized or performed by this request.

## Final archive and preservation readback

All 8 tasks are complete. Six requirement blocks in three canonical capabilities exactly match the archived deltas. Archive is `2026-10-09-repair-five-lifecycle-history-contracts`; strict canonical validation after archive passes 68/68. Scoped Ruff/format (14 files), ty and all applicable architecture/cancellation/timing/settings/simplicity checks pass. Final whitespace check passes. Exactly five own source rows were updated and reread; all 333 other rows are byte-identical. Of 38 baseline dirty files, all 37 outside the intentionally shared registry remain byte-identical. The registry retains their prior summaries and evidence. Local HEAD remains the initial SHA; no publication occurred. See [closure.json](closure.json) for final hashes and checks.
