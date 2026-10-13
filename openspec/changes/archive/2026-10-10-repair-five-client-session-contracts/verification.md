# Verification: five client/session contracts

Date: 2026-10-10 (Europe/Kiev). Source: `main`, HEAD `7e3779ffaea1a27c29710a7d496e8fa037131f98`, plus preserved pre-existing working changes. Exactly five selected source rows, all initially `НЕ ПРОВЕРЕНО`: UP-ISSUE-1636, UP-PR-2323, UP-ISSUE-2311, UP-ISSUE-2498 and UP-PR-2516.

## Result and evidence

| Source row | Independently established local result | Evidence |
| --- | --- | --- |
| UP-ISSUE-1636 | Added missing read-only preview and confirmed ID-scoped repair. Prior whole-home bounded reads/grouped queries/progress retained and revalidated. | New CLI suite: 30 PASS; existing retag and operator-data tests in the 111-test selection. |
| UP-PR-2323 | Added the actual preview/repair commands, fresh selected identity/provider checks, backup, JSON output, indexed discovery and partial-failure diagnostics. | CLI mismatch/repair, transcript/config/unrelated preservation, unsupported/ambiguous/missing IDs, WAL stale values, backup failures and both fallback paths. |
| UP-ISSUE-2311 | Existing primary READMEs, guide and downloadable profiles use Astra; primary full configurations keep xhigh. The 872k instructions remain GPT-5.6-specific. | Parsed TOML and contextual checks saved in `examples.json`; all existing example tests PASS. |
| UP-ISSUE-2498 | All five ordinary provider blocks already enable standalone search and identify codex-lb >= 1.22.0. | Parsed examples and explanation of live-search preference versus experimental feature flag. |
| UP-PR-2516 | English/Chinese README, both ordinary guide blocks and downloadable ordinary provider independently verified. Separate Daybreak policy preserved. | Five parsed blocks; source files unchanged byte-for-byte from baseline. |

The new CLI tests were run before implementation: **7 FAIL** on absent `preview`/`repair` commands. Final combined selection: **111 PASS, 0 skips, 0 xfails**, including **30 new CLI tests**. After closing test-fixture SQLite handles explicitly, the changed CLI suite was rerun: **30 PASS**. These are repeated validations of the same cases, not 141 distinct tests.

Commands:

```text
uv run pytest tests/unit/test_codex_session_metadata_cli.py tests/unit/test_codex_sessions_retag.py tests/unit/test_cli.py tests/unit/test_operator_data_batch.py tests/unit/test_client_setup_examples.py -q --tb=short --junitxml=.git/batch-client-session-20261010/tests.xml
uv run pytest tests/unit/test_codex_session_metadata_cli.py -q --tb=short
uv run ruff check app/cli.py app/codex_sessions_repair.py tests/unit/test_codex_session_metadata_cli.py
uv run ruff format --check app/cli.py app/codex_sessions_repair.py tests/unit/test_codex_session_metadata_cli.py
uv run ty check app/cli.py app/codex_sessions_repair.py tests/unit/test_codex_session_metadata_cli.py
uv run python scripts/check_proxy_architecture.py
uv run python scripts/check_cancellation_safety.py
uv run python scripts/check_proxy_timing_seams.py
uv run python scripts/check_settings_tiers.py
uv run python scripts/check_migration_topology.py
npx --yes @fission-ai/openspec@1.11.0 validate repair-five-client-session-contracts --strict
npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict
uv run --group docs mkdocs build --strict
git diff --check
```

Scoped Ruff/format/ty, all five repository guards and strict documentation build PASS. Strict canonical OpenSpec: **68/68 PASS**. Change validation PASS. The migration guard checks the current local `origin/main` reference; this batch adds no migration and does not assert freshly fetched remote parity. OpenSpec instructions emit the pre-existing `context_docs` rules warning; validation succeeds.

The installed `uv run codex-lb` entrypoint independently completed `preview → repair → preview` against a disposable synthetic home, moved mismatch to consistent, emitted separate JSON/progress and preserved an opaque non-UTF-8 transcript tail. The initial smoke harness forgot to close its own SQLite connection during cleanup; that fixture was corrected and the smoke rerun, including successful cleanup. One initial temporary `state_5.sqlite` remains outside the repository because automatic approval review rejected its removal with `blocked by policy`.

## Completeness, correctness and coherence

The two delta requirements are synchronized to canonical specs. All six repair scenarios have CLI boundary coverage, including indexed lookup without `rglob`, read-only preview without copy fallback, selected-row updates, unsupported/ambiguous refusal, stale metadata at backup/rewrite and separated JSON/progress. Existing retag tests cover bounded metadata, grouped discovery, transcript-preserving rewrite and progress/fallback behavior. Client documentation assertions independently establish the three already-implemented proposal scopes. The guide links the owning specification and records manual recovery constraints.

The implementation reuses existing retag backup/rewrite primitives and a shared progress reporter. No new dependency, server setting, database migration, README section or dashboard item is introduced. No critical or unresolved local verification findings remain. Final row readback and preservation counts are recorded in `closure.json`.

Code discovery used the existing codebase-memory graph and direct caller traces before editing. Two index refreshes reported success but did not expose newly added repair/progress symbols in subsequent searches; final impact verification therefore uses current source imports, the focused regressions and the installed CLI smoke. This graph gap does not establish graph completeness for new symbols.

## Boundaries

Evidence is local Windows with synthetic SQLite homes. No live Codex home was modified. Native WSL/Docker mounts, live providers/search, cloud synchronization, PostgreSQL/MySQL, distributed operation, full-repository pytest and hosted CI are not established. Repair is not a cross-file transaction: Codex must be closed; a partial failure preserves backups and does not automatically restore data over another writer. The previous registry partials and production/platform claims retain their scopes. No commit, push, PR, merge, release or deployment occurred.
