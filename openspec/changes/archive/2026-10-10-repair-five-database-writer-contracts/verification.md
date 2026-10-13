# Verification: five database writer contracts

Client date: 2026-10-10. Initial and final source HEAD: `7e3779ffaea1a27c29710a7d496e8fa037131f98`, branch `main`. No commit, push, PR, merge, release or deployment. Exactly five selected registry records were initially `НЕ ПРОВЕРЕНО`: UP-ISSUE-2447, UP-ISSUE-1949, UP-ISSUE-1682, UP-ISSUE-1981, UP-PR-2460. Live upstream metadata is in [upstream-snapshot.json](upstream-snapshot.json).

## Contract mapping

| Record | Final behavior and evidence |
| --- | --- |
| UP-ISSUE-2447 | Auth attempt mutations and OAuth record/status writes use local admission. OAuth-owned session cleanup stays inside the section; upstream exchange stays outside. New real-file limiter/flow tests and HTTP password login/browser OAuth contention tests pass, alongside existing auth and OAuth API suites. |
| UP-ISSUE-1949 | Fingerprint attempt sessions open after local admission and close before its release. Matching and mismatching keys, transient lock retry, exhausted budget and private diagnostics retain existing behavior; real-file contention and replica guardrail suites pass. |
| UP-ISSUE-1682 | Admission reentrancy now checks the owning task, so inherited child contexts cannot bypass it. Cancelled waiters preserve the holder. Lease writes enter the gate with session cleanup inside, and retain database execution-time expiry. A cancelled real-file writer rolls back, then a new leader acquires/renews/releases; existing heartbeat/deadline, watchdog, teardown and leader tests pass. |
| UP-ISSUE-1981 | Reclamation owns an additional cleanup task before awaiting it. Caller cancellation is deferred through interruption/invalidation and callback registration; closed-driver interruption failure still attempts invalidation. Real SQLite next-writer recovery and cleanup registry drain pass. Existing healthy/closed/in-memory/PostgreSQL/grace/bounded teardown coverage passes. |
| UP-PR-2460 | Existing owner-before-key lock order and activation gate before mutation are independently confirmed. All three current API race tests pass on native PostgreSQL 16 and in the SQLite API suite. Makefile already includes those exact PostgreSQL targets. No duplicate cascade implementation added. |

## Reproduction and corrections

Before runtime edits, `tests/unit/test_database_writer_contracts.py` produced **12 failed, 3 passed**: inherited-child admission/cancelled waiter, auth admit/clear/sweep, OAuth record/status, four lease operations, and reclaim cancellation failed. [red.xml](red.xml) records the exact tests. The fingerprint and failed-attempt cases were controls; their pending-task check did not independently reproduce failure before the patch. The new final unit file has 16 cases, including one additional cancelled-writer-to-leader regression.

The first adjacent run encountered two test-harness assumptions and timed out after the leader stand-in failure. Its PostgreSQL stand-in retained the ambient SQLite configuration, causing admission to serialize scripted renewal calls and making its call-count assertion fail before its cleanup. The stand-in now selects matching PostgreSQL/in-memory configuration. A real reclaim test expected `invalidated` to stay true even after the now-owned late close had completed; it now accepts the fully closed connection. Both preserve the tested product invariant. The corrected complete aggregate is green; the earlier aborted aggregate is not counted as green.

## Exact checks

| Command/selection | Result |
| --- | --- |
| `uv run --frozen pytest tests/unit/test_leader_election.py tests/unit/test_db_session.py tests/unit/test_db_rate_limiter.py tests/unit/test_startup_sentinel_lock_retry.py tests/unit/test_sqlite_lock_classification.py tests/unit/test_dashboard_users.py tests/unit/test_database_writer_contracts.py -q --tb=short --timeout=60 --timeout-method=thread --junitxml=openspec/changes/repair-five-database-writer-contracts/unit.xml` | **184 PASS, 2 SKIP** in 54.92s; [unit.xml](unit.xml), [unit-run.log](unit-run.log). |
| `uv run --frozen pytest tests/unit/test_database_writer_contracts.py -q --tb=short --timeout=20 --timeout-method=thread --junitxml=openspec/changes/repair-five-database-writer-contracts/green.xml` | **16 PASS** in 3.97s; [green.xml](green.xml). Fifteen overlap the aggregate, so final distinct unit passes = **185**. |
| `uv run --frozen pytest tests/integration/test_oauth_flow.py tests/integration/test_dashboard_password_auth.py tests/integration/test_replica_guardrails.py tests/integration/test_dashboard_users_api.py tests/integration/test_auth_sqlite_writer_contracts.py -q --tb=short --timeout=60 --timeout-method=thread --junitxml=openspec/changes/repair-five-database-writer-contracts/sqlite-integration.xml` | **146 PASS** in 148.93s; [sqlite-integration.xml](sqlite-integration.xml), [integration-run.log](integration-run.log). |
| Native PostgreSQL 16: `uv run --frozen pytest tests/integration/test_dashboard_users_api.py::test_key_reactivation_never_leaves_active_keys_on_a_disabled_owner tests/integration/test_dashboard_users_api.py::test_key_patch_that_also_renames_orders_the_owner_before_the_key tests/integration/test_dashboard_users_api.py::test_concurrent_admin_mutations_keep_exactly_one_admin -q --tb=short --timeout=120 --timeout-method=thread --junitxml=openspec/changes/repair-five-database-writer-contracts/postgres.xml` | **3 PASS** in 28.77s; [postgres.xml](postgres.xml). Isolated synthetic database, loopback-only container; no production database access. |
| `uv run --frozen ruff check` and `ruff format --check` for the five changed app files plus `tests/unit/test_database_writer_contracts.py`, `tests/unit/test_db_session.py`, `tests/unit/test_leader_election.py`, `tests/integration/test_auth_sqlite_writer_contracts.py` | PASS; **9 files** formatted. |
| `uv run --frozen ty check` for the same nine files | PASS. |
| `uv run --frozen python scripts/check_proxy_architecture.py`, `scripts/check_cancellation_safety.py`, `scripts/check_proxy_timing_seams.py`, `scripts/check_settings_tiers.py`, `scripts/check_migration_topology.py`, `.github/scripts/check_simplicity_budgets.py` | All PASS. 98/98 setting fields; 274 revisions, single head `20261009_010000_add_account_window_reserves`. The initial guessed simplicity script path did not exist; the canonical `.github/scripts/` check passed. No migration/settings/UI surface added. |
| `npx --yes @fission-ai/openspec@1.11.0 validate repair-five-database-writer-contracts --strict`; `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict` | Change PASS; **68/68 main specs PASS**. |
| Graph impact discovery plus current-source admission audit | All 29 app files using admission inspected; no direct task spawning, gather, shield or deferred-cancellation helper inside their write sections. Dynamic dispatch remains outside this static observation. |
| `git diff --check` and saved registry/hash closure | PASS; [closure.json](closure.json). |

Final distinct SQLite passes: **331** (185 unit + 146 integration); PostgreSQL: **3** additional backend executions. No duplicate focused runs are counted twice.

## Completeness, correctness and coherence

All five contracts map to code and test evidence above. Three added requirements and the complete modified startup requirement are synced into [database-backends](../../../specs/database-backends/spec.md), with stable rationale/example in its context. No critical or warning findings remain in the verified local scope. Registry count, saved-row readback and dirty-work preservation are recorded in closure.json before archiving. The reviewed implementation uses the existing admission primitive, cancellation helper, database clocks and owner-lock order.

## Residual scope

Two `uvloop` cases are skipped on Windows because uvloop is unavailable. Historical macOS/Windows incident timing, native zombie handles that cannot be reclaimed, continuous production streaming, real provider behavior, cross-process/distributed throughput, cloud CI and whole-repository tests are not established here. Driver invalidation failure retains diagnostics/owned cleanup and does not promise guaranteed native recovery or automatic process restart. These are local contract closures; no release/deployment/public or current-head cloud merge readiness claim is made. Existing unrelated partials and external residuals remain unchanged.
