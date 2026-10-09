# Verification: five operator data contracts

Date: 2026-10-09, Europe/Kiev. Base local main: `005c8aa4d06be1d0d2f1ccdb2e0f90b725884f8e`.

Exactly five initially unverified records: **UP-PR-2325, UP-PR-2322, UP-PR-2307, UP-PR-2518 and UP-PR-2522**. Initial own rows, live GitHub identities/heads and 73 prior dirty file hashes are in [source-snapshot.json](source-snapshot.json). Upstream PR bodies and author counts are context, not verification evidence.

## Findings and resulting behavior

| Record | Independent finding and repair/verification | Evidence |
|---|---|---|
| UP-PR-2325 | Existing retag repeatedly scanned full transcripts and counted provider-like transcript fields. It now reads bounded leading metadata, uses one grouped SQLite planning count, reuses targeted discovery observations, preserves opaque tail bytes, verifies planned targets, and reports retained backups on partial failure. JSONL hard-link snapshots, SQLite online backups and the existing write fallback remain. CLI phase JSON goes to stderr. A real Windows closed-pipe process exposed CRT OSError/EINVAL in addition to BrokenPipeError; the narrow handling now permits exit 0 without swallowing other I/O errors. Obsolete per-provider counting helpers were removed; existing URI/fallback tests exercise the grouped path. | Initial malformed/oversized/opaque and missing-progress failures; dry-run reads exactly 65,536 bytes and runs one grouped COUNT; partial backup/write controls; all five closed-progress phases; actual Windows subprocess, targeted identity refusal, legacy incomplete tail and existing CLI/retag regressions. |
| UP-PR-2322 | Unknown newer ledger revisions lacked conditional rollback-image recovery guidance. The existing refusal now explains compatibility, ended transactions, recoverable DB/key, both revisions in the executing build and the same target database. No automated stamp or relaxed validation is added. | Actual upgrade refusal and unknown stamp leave a disposable SQLite file byte-identical. Existing schema-ahead/unsupported-revision controls pass. Scope remains recovery guidance only, not all of issue #1470. |
| UP-PR-2307 | The online runner lacked starts, elapsed execution and failure progress. A small iterator adapter logs revision identity/direction only, restores its original callback in finally, propagates the original exception and retains Alembic transactions/version bookkeeping. CLI progress is enabled on stderr with the existing stdout result. | Actual online upgrade/downgrade/no-op, real CLI subprocess, failed step observing its own start, same exception identity, no later execution, privacy and callback restoration; broad existing runner/serialization controls. Executed does not assert transaction commit. |
| UP-PR-2518 | The historical merge and current single head already exist. Added populated-parent coverage verifies both exact parents, merge ancestry, demultiplexed downgrade ledger, identical merged schema, preserved request/SCIM rows and re-upgrade through the current head with policy/drift checks. | Both new branch cases and the existing historical merge regression pass. No published migration or contributor metadata was rewritten. This is local graph/data/test scope. |
| UP-PR-2522 | Existing source contains both facet indexes, PostgreSQL concurrent invalid-index repair, MySQL/MariaDB GROUP BY enumeration and the earliest-row probe. No repository rewrite was justified by SQLite reproduction. | Actual facet migration is idempotent and downgrades/re-upgrades without losing rows; index column order and SQLite earliest-row index plan match the contract. Eight earliest-row oracle cases cover NULL/ordinary/warmup/limit_warmup and deleted rows. Real options API matches visibility/NULL/status semantics and uses 1,400/1,200 SQLite VM operations on the existing 20,000-row fixtures. Live PostgreSQL/MySQL plans remain external. |

## Reproduction and final commands

[Initial red evidence](red-before.log): eight failures before implementation. Initial development harness mistakes (a too-long parameter ID and later reversed Alembic walk arguments/list-versus-tuple expectations) were corrected; they are not product findings. The initial pytest-captured CLI stderr test was replaced by the real subprocess test because pytest already owns root logging handlers.

```powershell
uv run pytest tests/unit/test_operator_data_batch.py tests/unit/test_codex_sessions_retag.py tests/unit/test_cli.py tests/unit/test_db_migrate.py tests/integration/test_operator_data_batch.py tests/integration/test_migration_serialization.py tests/integration/test_migrations.py::test_scim_and_overflow_retirement_lineage_is_single_and_round_trips tests/integration/test_request_log_facet_sqlite.py tests/test_request_logs_options_api.py -q --tb=short --junitxml=openspec/changes/repair-five-operator-data-contracts/focused.xml
# 188 passed, 6 skipped, 1 failed, 17 warnings; 395.37s.

uv run pytest tests/unit/test_operator_data_batch.py tests/unit/test_codex_sessions_retag.py tests/unit/test_cli.py -q --tb=short --junitxml=openspec/changes/repair-five-operator-data-contracts/retag-final.xml
# 78 passed, 1 warning; 9.75s after removing obsolete counting helpers.
```

The second run repeats a subset and is not added to the first: **188 distinct passing tests**, including all 32 new boundary tests. The aggregate is not fully green. Its one failure is `test_create_sqlite_pre_migration_backup_preserves_source_mode`: Windows returns mode 0666 after chmod(0600). The same test exported from the unchanged HEAD fails against unchanged `app/db/backup.py`; see [baseline-windows-mode.log](baseline-windows-mode.log). This separate platform residual is outside the five selected records, and neither the backup code nor that test was changed or silently skipped.

The six explicit skips are PostgreSQL concurrent migration, advisory lock and query-plan controls, plus MySQL concurrent migration and named lock controls. SQLite file-backed data and real Windows CLI evidence do not certify these engines, POSIX filesystem permissions, provider clients, public artifacts, cloud CI or production. Reflection, Starlette deprecation and JUnit property warnings are reported separately from failures.

Scoped Ruff lint/format and ty cover six app files and three test files. Architecture, cancellation safety, timing seams, settings tiers, migration topology (272 revisions, one current head), simplicity budgets, strict MkDocs and strict OpenSpec validation pass. All 68 canonical specs pass after syncing four added requirements. Final check results and preservation counts are in closure.json.

## OpenSpec verification

Completeness: the eight tasks are completed after registry/archive readback. Correctness: four requirements and ten scenarios map to the public CLI, file-backed data, revision adapter and original-failure tests described above. Coherence: fixed bounds, optional progress, owned backups and original Alembic execution remain as designed; no settings, dependencies, migration revisions or dashboard pixels were added. Stable rationale, failure modes and examples are in the canonical contexts and existing operator guides. No unimplemented requirement or unexplained local scenario gap remains.

Graph navigation mapped original CLI, migration and facet callers before editing. A fast index refresh was attempted without persistence, but its returned graph still omitted the new untracked symbols; integration tests are also excluded by index policy. New symbols and those test paths were therefore checked directly in current source. Graph edges inferred only from names were treated as navigation hints, not runtime proof.

## Preservation and publication limits

The initial tree contained 73 dirty files from previous packages. Exactly the shared registry is intentionally edited; all 72 other initial dirty files are retained byte-for-byte, including the query-caching spec/context. All 333 other source rows remain byte-identical, and their prior summaries and external residuals are retained. This request authorizes local repair and verification only: no commit, push, PR, merge, release or deployment is performed. The local HEAD remains the initial SHA.
