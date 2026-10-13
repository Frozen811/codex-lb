# Verification: complete account window reserves

2026-10-09, Europe/Kiev. Continuation of the original exact-five batch; only UP-PR-1528 was still partial. Original HEAD and current HEAD: `7e3779ffaea1a27c29710a7d496e8fa037131f98`. No branch, commit, push, PR, release or deployment.

## Result

The shared reserve, optional 5-hour/weekly overrides, atomic disable/remove, fresh telemetry gate, current-owner dispatch checks and faithful reserve/usable display are implemented. This completes the declared local implementation of UP-PR-1528. The other four selected tasks remain closed and their own registry rows and archived evidence are unchanged.

Implementation adapted from NikitaMGrimm's upstream PR [#1528](https://github.com/Soju06/codex-lb/pull/1528), head `caf31b77a4ef85047459635e956fdd62f7fbd7ce`, base `f8ffbac2099a113fba54dfd8d77774f5bca80ffa`. aaravrav is credited there for the complementary reserve design. Upstream CI/dependency updates and historical migration branches were excluded. `merge-plan.json` records exact selected files, base/head and integration staging. Published migration history was not rewritten.

Fork adaptations preserve strict credential rejection, usable reauth warnings in manual warm-up, retained reset evidence, plain warm-up fallback, paused reset-credit observation and idempotent backup. Legacy `/quota-limit` feeds the shared policy; zero remains blocked through fresh authorization. Backup includes policy/overrides. MySQL uses UPDATE plus a locked projection rather than unsupported UPDATE RETURNING. Unavailable peers do not determine the best health tier but still provide canonical backoff context. Input-change retries are bounded at eight; perpetual churn refuses admission, releases every lease and publishes no affinity.

## Runtime checks

- Main combined selection (`final-backend.xml`): **4752 passed, 25 skipped, zero failures**, 452.02 s, exit 0. Includes HTTP/bridge/WebSocket, current-owner selection/concurrency, synthetic/planner warm-up, usage/refresh/live ingestion, reserve computation, cancellation/settlement and SQLite forward migration. Exact file lists are in `test-selections.json`; invocation is `uv run pytest -q -n 3 <final-backend files> --tb=short --junitxml=.../final-backend.xml`.
- Prior package (`prior-package.xml`): **256 passed, zero skips/failures**, 123.04 s, exit 0. Reset-credit API/mapper/scheduler/store, accounts read/backup, settings and preceding migration recovery.
- Migration compatibility (`migration-compat.xml`): **29 passed**; explicit admission bounds (`admission-bounds.xml`): **16 passed**. They overlap main/prior selections. The union is **5017 distinct SQLite Python passes**, not the sum of all diagnostic reruns.
- Frontend: `bun run test src/features/accounts src/features/dashboard src/components/usage-quota-bar.test.tsx src/__integration__/account-usage-limit-flow.test.tsx src/test/mocks/usage-limit-handler.test.ts src/features/settings/schemas.test.ts src/features/settings/components/routing-settings.test.tsx`: **692 passed, 51 files**, exit 0. `bun run build` (TypeScript + Vite) and `bun run lint`: exit 0.
- Local PostgreSQL 16 (`postgresql.xml`): **20 passed, 2 opposite-backend skips**. Local MySQL 8.4 (`mysql.xml`): **20 passed, 2 opposite-backend skips**. Both verify policy API/fresh owner state, empty-database upgrade/policy/drift and reserve backfill/downgrade/replay with credential preservation. These backend-specific executions overlap logical tests and are reported separately.
- Server fixture initially created head ORM metadata without a ledger; fixture setup now explicitly verifies that schema and initializes the sufficiently wide ledger before downgrade. Diagnostic setup failures are not counted as passes. The production migration code was not weakened or altered to conceal them.
- The temporary local Docker containers bound only loopback ports, used no existing stack, and were removed along with ephemeral credential files. Image IDs/digests and removal proof are in `server-evidence.json`. `test-selections.json` lists server selection; the filter was `usage_limit or combined_usage_policy or server_reserve or migration_contract_policy_and_drift_match or upgrade_head_from_empty_database`.

## Visual and structural checks

Synthetic `example.invalid` account data rendered in baseline and current app through intercepted API responses. Browser captures: [before](screenshots/before-accounts.png), [after](screenshots/after-accounts.png), [reserve editor](screenshots/after-reserve-editor.png). Both overview and editor inspected: provider 82% remaining / 40% reserved / 42% usable for the short window, and 70% / 20% / 50% weekly. The shared and separate reserve controls are visible, and the footer does not obscure the full-page capture. Local Vite helpers were stopped after capture.

`uv run ty check`, `uv run ruff check .`, `uv run ruff format --check .` (1527 files), architecture/cancellation/timing/settings guards, simplicity budgets and migration topology passed. One connected 274-revision head, `20261009_010000_add_account_window_reserves`; two new forward revisions across the entire five-task package on fresh fork/main. No new environment variable or navigation item. `git diff --check` passed.

Strict OpenSpec main validation **68/68 passed**; this change validates strictly. All declared delta requirements are synced. Normative code/API/transport/planner/migration requirements map to the selected tests; stable context records the fork adaptations and upstream attribution. All implementation tasks complete, no critical local correctness issue found. Archived completion is conditional on the saved registry/closure readback below.

## Preservation and limits

53 pre-continuation dirty files were copied and hashed before integration. **40 remain byte-identical; 13 shared files (including the registry) were intentionally adapted; no unexpected prior-file change**. The original four-task archive is unchanged. `preservation.json` and `preservation-result.json` contain evidence. Only UP-PR-1528 changes its registry row in this continuation; the original batch still contains exactly five records.

The 25 main-selection skips remain explicit: PostgreSQL query-plan/locking/advisory scenarios, Windows `tzset`, and three superseded T21 conflict schedules. Server smoke covers the stated native scenarios, not every skipped PostgreSQL test. Main diagnostic aggregates had failures during integration and cache-churn scheduling; the final combined run, with the current code and cleanup, passed without failures. Source fixtures retain the ownership/lease assertions; budget-boundary fixtures use the explicit retry budget. No full-repository pytest, production/provider, distributed deployment, public artifact, or cloud CI claim is made. Older partial registry entries/F-045/CI-04 are retained.
