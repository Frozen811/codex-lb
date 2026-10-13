# Verification: five migration/contributor contracts

Date: 2026-10-10 (Europe/Kiev). Checkout: `C:\codex-lb`, branch `main`, HEAD `7e3779ffaea1a27c29710a7d496e8fa037131f98` plus preserved pre-existing changes. Exactly five initial `НЕ ПРОВЕРЕНО` source rows: UP-ISSUE-2474, UP-PR-2461, UP-PR-2462, UP-ISSUE-1471 and UP-ISSUE-2309. Initial dirty-file hash snapshot: 430 files. No application, migration or dependency file was edited by this batch.

## Result and source mapping

| Source | Local result | Evidence |
| --- | --- | --- |
| UP-ISSUE-2474 | Existing September merge independently validated; collision exemption fixed to require exact published identities and actual convergence. | Three populated starts (SCIM, overflow, both-parent ledger), downgrade/re-upgrade, current head and schema drift assertions; topology regressions. |
| UP-PR-2461 | Published empty merge retained with both original parents and populated-row preservation. | Single-head graph, both stamps after merge reversal, identical table set, historical request row retained through current head. |
| UP-PR-2462 | Single-head lineage outcome established through the published merge. The rejected proposal's restamping/reparenting method is intentionally not adopted. | Original revision files untouched; both published paths converge and upgrade to current head. Equivalent fork behavior does not claim that this upstream PR was merged. |
| UP-ISSUE-1471 | Replaced ineffective SQL checks and Python-list simulation with static safety lint plus real PostgreSQL fixture/timing gate, failure artifacts, timeout, and dedicated scheduled/path/manual workflow. | 3,000,000 seeded PostgreSQL rows; four actual pending migrations; real timeout negative control; SQLite CLI budget and actual failing-revision regressions. |
| UP-ISSUE-2309 | Consolidated repeated OpenSpec instructions and clarified exact scope, evidence readback, authorized completion, pre-import test storage and affected public transports while preserving contributor/merge gates. | Direct AGENTS diff, current `tests/conftest.py` and `tests/runtime.py` isolation order, canonical requirement/context and official reference links. No prose-mirroring tests added. |

Live read-only GitHub source retrieval confirmed the issue/PR descriptions. UP-ISSUE-1471 and UP-ISSUE-2309 remain open upstream; UP-ISSUE-2474 is closed. PR2461 is merged; PR2462 is closed without merge. Local registry closure does not change those states.

## Tests and checks

Initial red run: **12 substantive failures** (missed updates/list benchmark and three collision holes), plus one existing topology test assumption that disk equaled HEAD despite three prior uncommitted revisions. The latter test now compares HEAD's revision edges with the matching disk identities. A subsequent SQL-resolution review exposed **three additional red cases** for annotations, static f-strings and later variable reassignment; the conservative resolver fixed them. Negative/unrelated bounds also remain rejected.

Final evidence is **57 distinct pytest passes, 0 skips/xfails**. `tests.xml` records a 52-test combined pass; `static-final.xml` records the 43 final static/topology passes, including five added boundary cases. Their union contains 57 tests; repeated cases are not counted twice. The three populated lineage cases and eleven database benchmark cases remain unchanged from the combined run. A pre-existing Starlette/AnyIO deprecation warning remains.

```text
uv run pytest tests/unit/test_migration_duration_gate.py tests/unit/test_check_migration_topology.py tests/integration/test_september_lineage.py tests/integration/test_migration_duration_benchmark.py -q --tb=short --junitxml=.git/migration-benchmark/tests.xml
uv run pytest tests/unit/test_migration_duration_gate.py tests/unit/test_check_migration_topology.py -q --tb=short --junitxml=.git/migration-benchmark/static-final.xml
uv run ruff check scripts/check_migration_durations.py scripts/benchmark_migrations.py tests/unit/test_migration_duration_gate.py tests/unit/test_check_migration_topology.py tests/integration/test_september_lineage.py tests/integration/test_migration_duration_benchmark.py
uv run ruff format --check <the same six Python paths>
uv run ty check <the same six Python paths>
uv run python scripts/check_migration_topology.py
uv run python scripts/check_migration_durations.py
uv run python scripts/check_proxy_architecture.py
uv run python scripts/check_cancellation_safety.py
uv run python scripts/check_proxy_timing_seams.py
uv run python scripts/check_settings_tiers.py
uv run python .github/scripts/check_simplicity_budgets.py
npx --yes @fission-ai/openspec@1.11.0 validate repair-five-migration-contributor-contracts --strict
npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict
git -c core.safecrlf=false diff --check
```

Scoped Ruff/format/ty and all listed repository checks PASS. Current topology: 275 revisions and one head, `20261010_000000_add_source_catalog_discovery`. The guard reads the existing local `origin/main` ref; this batch adds no migration and does not assert fresh remote parity. Strict OpenSpec change validation PASS and canonical specs **68/68 PASS**. Workflow YAML parse and event/job/command inspection PASS. Initial strict change validation caught an omitted existing clean-check scenario; it was restored before synchronization. OpenSpec's existing `context_docs` rules warning is independent of successful validation.

## Actual database evidence

The PostgreSQL server was an isolated local WSL Docker `postgres:15-alpine` container running PostgreSQL 15.19, with Windows psycopg execution. The first container stopped because its WSL invocation ended; a bounded WSL keepalive enabled stable local execution. The initial small fixture exposed psycopg's ambiguous smallint `generate_series` overload; explicit integer casts fixed the real backend path before the production-scale run.

```text
uv run python -m scripts.benchmark_migrations --base-ref v1.25.1 --output .git/migration-benchmark/production-scale.json --summary .git/migration-benchmark/production-scale.md
```

The server URL came from `MIGRATION_BENCHMARK_SERVER_URL`; reports contain no URL, password, SQL or exception text. The runner created a unique database, upgraded to `20260928_020000_add_request_logs_facet_indexes`, seeded and counted **3,000,000 rows**, analyzed the table, and ran the normal migration runner to current head. Setup and fixture generation are excluded from revision timings. `production-scale.json` preserves actual times: approximately 0.003891, 0.030375, 0.020189 and 0.012318 seconds for the four pending revisions, all below 30 seconds.

`postgres-timeout-control.json` records an injected real migration SQL statement (`pg_sleep(0.2)`) under a 10 ms PostgreSQL statement budget: the first pending revision failed after about 0.011924 seconds, retained its failed timing and returned a failed report. Cleanup completed. Independent PostgreSQL catalog inspection found zero remaining runner-created databases. A CLI `nan` budget was rejected before storage/artifact creation. The test CLI's tiny finite budget similarly exits non-zero with genuine executed timings and retained JSON/Markdown output. The default fixture size and budget live only in the benchmark script.

## Completeness, correctness and coherence

All proposed implementation tasks are covered by product-boundary static CLI tests, real Alembic/database execution and direct instruction review. Existing migration progress is reused and its logger state restored; published migrations and application settings remain untouched. Both delta specs are synchronized, with original scenarios retained; stable rationale/examples are in the owning context files. No new runtime setting, dependency, README section or dashboard item is introduced. No unresolved local correctness finding remains. `closure.json` records exact row readback and byte-preservation results.

## Boundaries

Local evidence consists of Windows SQLite fixtures and isolated PostgreSQL 15.19 synthetic storage. It does not establish actual production timing, a complete historical migration range, PostgreSQL 16 hosted execution, MySQL execution, distributed/live/provider results, or full-repository pytest. Arbitrary dynamic SQL/SQLAlchemy expression trees are outside the static resolver and depend on actual duration execution. UP-ISSUE-1470's background data phases are not part of these five rows and retain their prior status.

The new workflow is checked in locally but has not run in GitHub; required branch-protection configuration and `CI Required` are not claimed. No commit, push, PR, merge, release or deployment occurred. The final registry readback confirms exactly five updated rows and preserves the other 333 source rows and unrelated prior dirty files.
