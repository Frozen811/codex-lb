# Five model-source registry contracts — 2026-10-10

Source HEAD: `7e3779ffaea1a27c29710a7d496e8fa037131f98` plus preserved local work. Exactly five selected records: UP-ISSUE-2318, UP-PR-2324, UP-ISSUE-2290, UP-PR-2305 and UP-PR-1905.

## Record disposition

| Record | Verified result | Boundary |
|---|---|---|
| [UP-ISSUE-2318](https://github.com/Soju06/codex-lb/issues/2318) | Original source-compaction forwarding proposal is **not applicable** to the fork's current clean-refusal contract. Both explicit endpoints, slash aliases and terminal Codex requests refuse before admission, accounting or dispatch. | Forwarding is not implemented. The historical ISSUES.md claim described refusal as resolution; this registry now states the mismatch explicitly. |
| [UP-PR-2324](https://github.com/Soju06/codex-lb/pull/2324) | Same proposal incompatibility, independently verified against `responses-api-compat` and current `test_source_compaction_refusal.py`. | Proposed forwarding patch was not imported. Existing UP-PR-2451 behavior remains authoritative. |
| [UP-ISSUE-2290](https://github.com/Soju06/codex-lb/issues/2290) | Implemented configure-once CPA discovery, inference credentials/client version, real HTTP catalogs, public/Codex catalog exposure and Responses dispatch without subscription accounts. | Live CPA/provider acceptance remains external. Catalog claims do not prove provider capabilities. |
| [UP-PR-2305](https://github.com/Soju06/codex-lb/pull/2305) | Implemented complete typed snapshot validation, four workers/five seconds/1 MiB, durable omission/restoration, independent manual pause, SQL revision fencing and worker/HTTP cancellation ownership. One linear forward migration on the fork's current parent. | No upstream merge revisions, new environment toggle, dependency, frontend navigation or deployment integration imported. |
| [UP-PR-1905](https://github.com/Soju06/codex-lb/pull/1905) | Corrected native owner reconciliation after disabled/unavailable source lookup. Both HTTP paths preserve response/file ownership across enabled, disabled and unavailable source states. Existing source WS guards and native compact settlement paths verified. | Synthetic upstreams and adapter doubles are local evidence. Native source WS transport and durable external-source reference revisions remain separate features. |

## Reproduction and corrections

- Initial API regression failed because catalogMode did not exist; historical CPA helpers had no runtime caller.
- Reinstating the former early lookup-miss return caused the two public disabled-source/native-response-owner cases to fail; file controls passed. The new reconciliation fixes both failures.
- The first 531-case aggregate had 529 PASS and two stale WS fixture failures. One replaced the recorder under observation; another omitted its proven owner from the fake pool. Both fixtures are corrected without weakening ownership assertions.
- A historical account-reserve test compared an old revision with today's full ORM. It now upgrades to head before its two full-schema comparisons while retaining all reserve/backfill/replay/downgrade assertions.
- PostgreSQL exposed a naive-clock test file pin that was already expired in its timezone-aware column. The final fixture claims the pin through the production repository and database clock. All owner assertions remain intact.

## Final verification

| Check | Evidence |
|---|---|
| Focused SQLite aggregate, 15 selected modules/targets, four isolated workers | **536 PASS**, zero failures/errors/skips/xfails; [sqlite-final.xml](sqlite-final.xml). |
| Final file-pin fixture recheck, overlapping both HTTP paths and all source states | **12 PASS**, already included in distinct SQLite total; [owner-final.xml](owner-final.xml). |
| Disposable PostgreSQL 16, configure-once discovery, ownership and server migration lifecycle | **35 PASS**, zero failures/errors/skips/xfails; [postgres-final.xml](postgres-final.xml). |
| Disposable MySQL 8.4, same contracts | **35 PASS**, zero failures/errors/skips/xfails; [mysql-final.xml](mysql-final.xml). |
| Historical SQLite migration | Full parent upgrade, preserved credential/paused row, default backfill, restamping/replay, downgrade/re-upgrade and ORM drift coverage in the aggregate. Server lifecycle covers both SQL backends. |
| CLI disposable SQLite upgrade/check | Upgrade head succeeds; migration_policy=ok and schema_drift=none; [cli-check.log](cli-check.log). |
| Fifteen changed Python paths: Ruff, format and ty | All PASS; [static.log](static.log). |
| Architecture, cancellation, timing, settings, migration topology and simplicity | All PASS; [guards.log](guards.log). Single 275-revision head, 98/98 classified settings; no new environment field. |
| OpenSpec 1.11.0 | Strict change PASS; all **68/68** main specs PASS; [openspec-change.log](openspec-change.log), [openspec-specs.log](openspec-specs.log). |
| Registry and previous-work preservation | Exactly five own source rows changed; 333 other source rows remain identical. See [closure.json](closure.json) and [initial-manifest.json](initial-manifest.json). |

The SQLite runs overlap and are not added together. Backend counts describe separate database executions, not additional distinct product scenarios. The initial failed evidence is superseded by passing final reports and remains described above rather than represented as green.

### Test commands

The aggregate used `uv run --no-sync pytest -q -n 4 --tb=short` with these exact targets and `--junitxml` pointing to sqlite-final.xml in the active change directory:

```text
tests/unit/test_model_sources_catalog.py
tests/unit/test_model_sources_service.py
tests/unit/test_model_sources_forwarding.py
tests/unit/test_model_sources_projection.py
tests/unit/test_cpa_catalog.py
tests/unit/test_proxy_model_source_continuity.py
tests/unit/test_proxy_websocket_model_source_guard.py
tests/unit/test_model_refresh_scheduler.py
tests/integration/test_cpa_discovery_contracts.py
tests/integration/test_source_continuation_contracts.py
tests/integration/test_source_catalog_migration.py::test_historical_catalog_migration_upgrade_replay_and_rollback
tests/integration/test_source_compaction_refusal.py
tests/integration/test_model_source_routing.py
tests/integration/test_proxy_compact.py
tests/integration/test_account_window_reserve_migration.py
```

Each final server run used `uv run --no-sync pytest -q -n 2 --tb=short` with `CODEX_LB_TEST_DATABASE_URL` set to its disposable local backend and these targets:

```text
tests/integration/test_cpa_discovery_contracts.py
tests/integration/test_source_catalog_migration.py::test_server_catalog_migration_backfill_replay_and_rollback
tests/integration/test_source_continuation_contracts.py
```

The final overlapping SQLite owner recheck used only test_source_continuation_contracts.py with the same `-n 2` options. CLI smoke used `uv run --no-sync codex-lb-db --db-url <disposable-sqlite-url> upgrade head`, followed by `check`. Static commands were `uv run --no-sync ruff check`, `ruff format --check` and `ty check` on the fifteen modified Python paths. The six guard scripts in guards.log were run with `uv run --no-sync python`. OpenSpec commands were `npx --yes @fission-ai/openspec@1.11.0 validate repair-five-model-source-contracts --strict` and `validate --specs --strict`.

## Spec verification

Completeness: all nine tasks completed. Correctness: the added requirement and all six scenarios map to scheduled catalog/dispatch, invalid snapshot/outage, omission/restoration, edit/newer-claim fencing, native collision/owner and cancellation/budget tests. Coherence: independent task-owned sessions, durable snapshots, SQL fencing, existing leader cadence and a linear migration follow the design. Stable context and the complete delta requirement are synced to `model-source-routing` before archive. No critical local gap remains in the implemented scope; the two forwarding proposals explicitly remain unimplemented and are classified as not applicable.

## Preservation and external limits

The initial manifest contains 292 dirty files. Five were intentionally extended: models.py, proxy/api.py, the WS guard fixture, the historical reserve migration test and issues-check.md. The other **287** must retain their initial hashes. Existing models.py and proxy/api.py contents are independently reconstructed by removing only this batch's additions and compared with their initial hashes. The two test originals were saved before their small compatibility corrections. No prior changes were discarded.

All runtime verification uses isolated local databases, loopback source fixtures, synthetic credentials and scoped tests. There is no current cloud CI, release, public artifact, production throughput, real CPA/provider acceptance or deployment claim. Upstream acceptance of discovery/forwarding remains its own decision. Commit, push, PR, merge, release and deployment were not performed.
