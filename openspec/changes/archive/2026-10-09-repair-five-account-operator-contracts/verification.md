# Verification: five account operator contracts

Date: 2026-10-09 (Europe/Kiev). Base main: `7e3779ffaea1a27c29710a7d496e8fa037131f98`. Checkout initially clean; no commit, push, PR, release or deployment.

## Results and exact scope

| Registry task | Result | Contract evidence |
|---|---|---|
| UP-ISSUE-850 | Fixed and closed locally | Imported destination ID, explicit null alias/false warm-up, workspace round trip, repeated restore without duplicate creation, paused status. `test_account_operator_contracts.py` (unit and integration), `test_account_backup_restore.py`, `test_accounts_backup_and_quota.py`. Ordinary import keeps its slot policy; source ID requires matching identity. |
| UP-PR-1528 | Fixed locally; full upstream remains partial | Existing scalar quota cap now gates backoff fallback and standard-quota exemption. 16 selection boundaries and real `/v1/responses` / `/backend-api/codex/responses` zero-cap rejection; persisted GET/PUT/reset cap paths. Current upstream `caf31b77a4ef85047459635e956fdd62f7fbd7ce` includes per-window reserves, final dispatch fences, stale telemetry denial and reserved-credit UI/pace accounting beyond this scalar repair; those are not implemented or certified here. |
| UP-PR-2497 | Verified and closed locally | Existing paused observation required no code change. Real cached count/expiry, bulk denial, selected-account observation/401 retry/route and upstream errors, mapper and polling exclusions passed. Paused is retained; no consume or implicit activation. |
| UP-PR-2122 | Fixed and closed locally | Inclusive original-before usage floor, zero default, paid-to-Free matching monthly baseline, retained reset evidence, backend/frontend explicit-zero bounds and empty-input rejection. New forward revision preserves legacy 99-default column and values. SQLite upgrade/downgrade/reupgrade, drift, rewound-ledger policy preservation, incompatible-column rejection; DDL compilation for SQLite/PostgreSQL/MySQL. |
| UP-ISSUE-2514 | Fixed and closed locally | Real bulk HTTP tests with non-first consumed credit, authoritative remaining IDs, partial consume failure and independent later-account success. Post-consume read uses account route and refreshed credentials; CAS prevents a stale observation overwriting a newer generation. No synthetic remaining IDs. Existing single-credit/ledger/claim tests passed. |

## Runtime verification

- `focused-command.txt` records the complete focused Python selection. Final `focused.xml`: **414 passed, zero failures/errors/skips/xfails**, 101.48 seconds, exit 0. `test-counts.json` records per-module counts. Total is distinct tests; diagnostic reruns are not added.
- `bun run test src/features/settings/schemas.test.ts src/features/settings/payload.test.ts src/features/settings/components/routing-settings.test.tsx`: **92 passed** in three files, exit 0.
- `bun run typecheck`: exit 0.
- `bunx eslint src/features/settings/schemas.ts src/features/settings/schemas.test.ts src/features/settings/components/routing-settings.tsx src/features/settings/components/routing-settings.test.tsx src/test/mocks/factories.ts`: exit 0.
- Initial regression `red.xml`: 10 failed / 13 passed on the original implementation: six cap bypass/backoff cases, two backup identity/omission cases, two ignored-floor cases. Corrections to the new test fixtures were completed before recording this red result.
- An initial combined unit/integration diagnostic run also encountered Windows temporary-DB cleanup WinError 32. Final xdist selection completed successfully, including process cleanup. This is not hidden or counted as a passing diagnostic run.

## Static and structural verification

- `uv run ty check`, `uv run ruff check .`, `uv run ruff format --check .`: passed (1514 Python files formatted).
- `uv run python scripts/check_proxy_architecture.py`, `scripts/check_cancellation_safety.py`, `scripts/check_proxy_timing_seams.py`, `scripts/check_settings_tiers.py`: passed; 98/98 settings classified.
- `git fetch fork main` refreshed the actual fork baseline. `uv run python scripts/check_migration_topology.py --base-ref fork/main`: passed, 273 revisions, one head `20261009_000000_activate_reset_warmup_threshold`, one new revision. Default `origin/main` check also passed.
- Windows has no `make` command. All commands from `make lint` were executed directly, including architecture guards and whole-repository Ruff checks.
- `uv run python .github/scripts/check_simplicity_budgets.py`: passed; README 218/225 lines, headings 10/10, env lines 54/60, core navigation 5/5, root entries 0/0.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict`: **68/68 passed**. Strict validation of this change passed. Requirement and stable context changes synchronized to four capabilities; prior requirements retained, including paid-to-Free zero-floor semantics.
- `git diff --check`: passed. Exact row preservation and final HEAD are in `closure.json`.

## Limits

Full upstream #1528 reserve policy remains partial. No live provider, production, full-repository pytest, cloud/public CI, browser screenshots, or PostgreSQL/MySQL server execution is claimed. Server dialect evidence is DDL compilation only. Existing registry partials, F-045 and CI-04 remain unchanged. Source status/head snapshots are in `upstream-source.json`; local closure is independent of upstream merge state.

## OpenSpec assessment

Completeness: all seven bounded implementation/verification tasks fulfilled. Correctness: backup identity and state, cap fallback, paused read/redemption split, authoritative bulk IDs, active threshold/migration scenarios map to focused tests. Coherence: existing account service/repository and serialization mechanisms are retained; no environment switch, dependency, endpoint or navigation item added. No critical implementation issue remains in the declared local scope; external and broader upstream scope is retained above.
