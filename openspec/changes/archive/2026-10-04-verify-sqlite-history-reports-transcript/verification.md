# Verification: UP-ISSUE-2483 / UP-ISSUE-1901 / UP-ISSUE-2291

Date: 2026-10-04, Europe/Kiev. Base: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`. Exactly three initially unchecked source rows. Local SQLite scope; remote publication is the separately authorized final step.

## Results and mapping

| Item | Implementation / evidence | Local result |
|---|---|---|
| 2483 | `UsageRepository.bulk_history_since`, new projection integration suite, existing real dashboard parity and indexed query-plan checks | Four malformed cap regressions failed before the two-line guard; negative/bool/string accepted, float raised SQLite IntegrityError. All now reject with ValueError before backend selection. Dense 100,000-row fixture returns 1,280 snapshots across 20 accounts. Primary/secondary, legacy NULL primary, account cutoffs, deterministic ties, zero cap and three floor shapes pass. |
| 1901 | Existing reports repository/rollup/cache; new `test_dense_reports_contracts.py` public API fixture, existing report API/rollup tests | 543,000 successful requests: exact totals, conversations, cost, qualified samples and seven daily medians agree before/after folding. Cache hit succeeds with aggregate_summary forced to fail if called. No report runtime rewrite was necessary. Unsupported millisecond cold-report claim corrected in ISSUES.md. |
| 2291 | Existing batcher drain loop; new deterministic backlog unit suite and real persistence integration suite, existing batcher regressions | 320-event operation drains in ten 32-event writes; competing operations receive fair bounded passes, no interval waits intervene, refused/exception writes cannot stall other operations. Real SQLite rows_v1/chunks_v2 preserve ordered 320 events plus one completed terminal and reject stale owner epoch. No batcher runtime rewrite was necessary. |

Requirements: capped projection history, bounded speed work, fair continuous backlog. All six delta scenarios have coverage, including the existing ninety-day omission test. Main requirement blocks match the change deltas. No missing implementation, uncovered delta scenario or design contradiction found.

## Commands and observed results

Red-before:

```text
uv run --frozen pytest -q tests/integration/test_projection_history_contracts.py
4 failed: -1, True, 1.5, "64"
```

After the guard:

```text
uv run --frozen pytest -q -s tests/integration/test_projection_history_contracts.py tests/integration/test_dense_reports_contracts.py tests/unit/test_transcript_backlog_contracts.py
27 passed, no skip/failure, 72.92 s

uv run --frozen pytest -q -s tests/integration/test_transcript_persistence_contracts.py
2 passed, no skip/failure, 1.19 s

uv run --frozen pytest -q tests/unit/test_http_bridge_event_batcher.py tests/integration/test_reports_performance_api.py tests/integration/test_report_rollup.py
43 passed, no skip/failure, 35.65 s

uv run --frozen pytest -q tests/integration/test_projection_history_contracts.py tests/integration/test_transcript_persistence_contracts.py tests/unit/test_transcript_backlog_contracts.py tests/unit/test_dashboard_projection_history_cap.py tests/integration/test_usage_repository.py tests/integration/test_dashboard_overview.py -k "projection_history or transcript_backlog or history_cap or row_cap or capped_query_plan_is_indexed_sqlite or ewma_tail_cap_matches_uncapped_history"
39 passed, 57 deselected, no skip/failure, 13.39 s
```

Counts overlap and are not a whole-repository run. An earlier command supplied two `-k` arguments and therefore ran only the dashboard parity case (1 passed, 67 deselected); the explicit combined selection above supersedes it.

First dense API run on this host: raw **21.416 s**, folded **7.811 s**, cached **0.015 s**. Deterministic fake-writer runs: 416 successful events over 13 writes, or 14 including a single failed operation, drain **24–27 ms** with one initial wait. Timings are diagnostic measurements, not assertions or deployment guarantees.

Final scoped Ruff check and format (five code/test files), `ty check app/modules/usage/repository.py`, proxy architecture, cancellation safety, timing seams, settings tiers (98/98), migration topology (271 revisions, one head), and simplicity budgets pass. Strict OpenSpec 1.11.0 change validation and **68/68** main specs pass.

The isolated publication tree is built from git archive of the base plus only this package. Imports are verified to resolve inside that tree. Its scoped Ruff/format, explicit-venv ty, architecture/cancellation/timing/settings and strict 68/68 specs pass. Initial ty invocation selected the system interpreter and reported missing packages; explicit `--python C:\codex-lb\.venv` passed. The archive lacks Git metadata, so simplicity validation is rerun with read-only parent GIT_DIR and the isolated GIT_WORK_TREE; all budgets pass. These corrected setup attempts are not reported as green checks.

## Isolated publication verification

The final isolated run uses the existing Python 3.13 venv with PYTHONPATH pointing to the publication tree built from the base commit plus only this package:

```text
C:\codex-lb\.venv\Scripts\python.exe -X utf8 -m pytest -q -s tests/integration/test_projection_history_contracts.py tests/integration/test_dense_reports_contracts.py tests/integration/test_transcript_persistence_contracts.py tests/unit/test_transcript_backlog_contracts.py tests/unit/test_http_bridge_event_batcher.py tests/integration/test_reports_performance_api.py tests/integration/test_report_rollup.py tests/unit/test_dashboard_projection_history_cap.py tests/integration/test_dashboard_overview.py::test_dashboard_projections_ewma_tail_cap_matches_uncapped_history tests/integration/test_usage_repository.py::test_bulk_history_since_per_account_row_cap_keeps_newest_rows tests/integration/test_usage_repository.py::test_bulk_history_since_row_cap_all_recent_when_floor_covers_cutoff tests/integration/test_usage_repository.py::test_bulk_history_since_capped_query_plan_is_indexed_sqlite
81 passed, no skips/failures, 108.22 s
```

One existing Starlette/AnyIO deprecation warning. Second dense report measurements: raw **21.372 s**, folded **7.855 s**, cached **0.013 s**. The full set passes without the prior dirty runtime changes. Code/test files are byte-equal to the reviewed publication tree; overlapping documents are composed from HEAD plus this package only. No unrelated runtime changes are staged.

Final assessment: all eight local implementation/verification tasks complete, all three selected scopes locally closed, all six scenarios covered, no critical or warning implementation findings. Archive is performed after verification and spec synchronization. Remote commit/push SHA is reported by the final response, rather than embedded in its own content.

## Preservation and limitations

125 pre-existing dirty files were captured before edits. **119 remain byte-identical**. Six intended overlaps are ISSUES.md, issues-check.md, and the usage-refresh-policy/responses-api-compat spec/context pairs. Prior text is retained; this package replaces only three selected source claims, three selected registry rows and the latest summary, and appends its section/spec/context. Publication copies those edits onto HEAD documents and omits the earlier dirty audit packages. Fingerprints are in fingerprints.md.

No new migration, configuration, README section, core navigation item or dashboard rendering. Existing report rollup and batcher code is retained. PostgreSQL/MySQL parity, the reporter's ARM dataset, production RSS, live provider/client traffic, published images/packages and exact-head cloud CI/review remain outside this local verification. F-045/CI-04 are not closed. Exact speed medians still depend on retained raw evidence, and an explicit recent floor can return more rows than the tail cap.
