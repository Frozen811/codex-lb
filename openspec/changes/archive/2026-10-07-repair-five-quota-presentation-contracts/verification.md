# Five quota records — local verification

Date: **2026-10-07, Europe/Kiev**. Base: `352e58d9fc2189bd48639f411782d35931d56f76`, branch `work`; initial working tree clean. After verification, the user requested a commit on `main` and clarified that it should appear on GitHub. The package was rebased without conflicts onto the fetched `Frozen811/codex-lb:main` head `126c0323630c43b2bb3e4dacb38ca869883baa4c`; that newer firewall test/spec commit is preserved as its parent. The correcting SHA is the adding commit returned by `git log --diff-filter=A --format=%H -- openspec/changes/archive/2026-10-07-repair-five-quota-presentation-contracts/proposal.md`. Publication target: `Frozen811/codex-lb:main`, with a normal forward-only branch update. GitHub branch/commit state confirms publication separately; local tests do not establish cloud CI, release or deployment.

Exactly five initially unverified source records were selected: **UP-ISSUE-1918 / UP-ISSUE-1367 / UP-PR-2321 / UP-PR-2489 / UP-PR-2468**. [Initial rows and preservation hash](source-snapshot.json), [fresh upstream metadata](upstream-snapshot.json), [red regression summary](red-regressions.txt), [final Python result](python-final.txt), [frontend result](frontend-final.txt).

## Reproduction and corrections

The initial existing usage/account/planner subset passed **127 tests**. New API regressions, before product edits, produced **22 failures and 10 passes** on the pinned base. These are real FastAPI GET `/api/accounts` requests over isolated SQLite repositories, not helper-only assertions.

**F-083 — historical monthly classification.** Historical primary-slot records used `>= 40000` minutes and excluded Free accounts, while ingestion used the inclusive 40320–46080-minute band. A zero-duration secondary placeholder prevented promotion, and an unknown/nonweekly secondary could silently drop the primary quota. Account mapping now uses the shared duration classifier and the same absent/zero-secondary rule as ingestion. Out-of-band or ambiguous observations retain their original slots. Exhausted historical Free monthly observations now remain visible as Monthly 0 percent with the corresponding quota-exhausted summary status; two older assertions expecting hidden monthly evidence were updated to this contract.

**F-084 — unmeasured Team monthly credits.** The fork assigned Team 7560 monthly credits by copying its weekly estimate. That fabricated capacity also prevented newer short/weekly data from superseding stale monthly history in account summaries. Remove the monthly default, retain monthly percentages/reset metadata, and preserve explicit calibrated overrides. Existing routing, background recovery, poll freshness and planner warmup freshness use a shared monthly-support predicate, so removal of the estimate does not discard Team monthly evidence or clear an exhaustion hold. Credit-based share estimation still requires a numeric capacity.

## Coverage by selected record

| Record | Independently verified local scope |
|---|---|
| UP-ISSUE-1918 | Edu account summaries retain exhausted weekly quota for active and explicitly exhausted accounts without credit evidence. Existing `credits_has` or positive-balance overrides remain valid under the current spec. Real SQLite selection repeats exclude exhausted Edu owners with and without reset/block metadata; available post-block evidence recovers the same account. No exact Edu credit capacity is established from these tests. |
| UP-ISSUE-1367 | Historical Free/Team rows at both inclusive boundaries, 43200 and 43800 minutes, absent/zero secondary placeholders, monthly percentages/duration/reset, out-of-band durations and positive/unknown secondary controls. The actual unchanged dashboard renders the resulting Monthly 76 percent on desktop/mobile. |
| UP-PR-2321 | Current polling/live ingestion preserves Team 43200/43800 observations; no synthetic short/weekly windows or invented monthly credits. API upgrade/reverse-history cases and a measured override are covered. Separate SQLite selection proves Team monthly holds and recovery without a credit estimate. |
| UP-PR-2489 | Existing frontend implementation independently passes non-aligned observations, equivalent UTC offsets, elapsed-time interpolation, true zeros and newly arriving samples. Account changes reset smoothed state. The browser switches dual-window → monthly → dual-window on the same page, with only the selected account's windows shown. |
| UP-PR-2468 | Existing API rejects unknown and malformed timezone keys atomically; valid names are trimmed and omitted/null/blank updates are no-ops. Persisted malformed legacy keys remain stored while forecast/routing use the documented UTC fallback. Existing planner API and unit suites pass. |

## Final checks

The following final Python selection passed **884 tests**, with **four existing PostgreSQL-only lock tests skipped** under SQLite and one existing Starlette/AnyIO deprecation warning. Earlier red/green, baseline and follow-up selections overlap this run and are not added to its count.

```sh
.venv/bin/python -m pytest \
  tests/unit/test_usage.py tests/unit/test_usage_updater.py \
  tests/unit/test_account_mappers.py tests/unit/test_account_usage_trends.py \
  tests/unit/test_live_usage_ingest.py tests/unit/test_quota_planner.py \
  tests/unit/test_load_balancer.py tests/unit/test_usage_refresh_scheduler_recovery.py \
  tests/unit/test_limit_warmup.py tests/unit/test_api_key_usage_share.py \
  tests/unit/test_proxy_api_key_usage_share.py \
  tests/integration/test_accounts_api_extended.py tests/integration/test_live_usage_ingest.py \
  tests/integration/test_load_balancer_integration.py tests/integration/test_quota_planner_api.py -q
```

Frontend: **22 component tests PASS**:

```sh
cd frontend
node node_modules/vitest/vitest.mjs run \
  src/features/accounts/components/account-usage-panel.test.tsx \
  src/features/accounts/components/account-trend-chart.test.tsx \
  src/features/accounts/components/account-card.test.tsx \
  src/features/accounts/components/account-detail.test.tsx
node node_modules/@typescript/native/bin/tsc -b
node node_modules/vite/bin/vite.js build
node node_modules/eslint/bin/eslint.js browser-smoke/quota-contracts.config.ts browser-smoke/quota-contracts.spec.ts
```

Current browser evidence: **2 PASS** at 1440/390 px; the baseline capture has **2 separate PASS**. Both use the current built dashboard with synthetic account summary payloads captured from the before/after Python mapper and stubbed APIs. The captures prove local rendering and account switching, not live provider behavior. Quota percentages/window shapes in the payloads are also covered by the real API regression tests.

| Width | Before | After |
|---|---|---|
| Desktop | [before](evidence/before-monthly-1440.png) | [after](evidence/after-monthly-1440.png) |
| Mobile | [before](evidence/before-monthly-390.png) | [after](evidence/after-monthly-390.png) |

Browser reproduction after archive:

```sh
cd frontend
QUOTA_STAGE=after \
QUOTA_EVIDENCE_DIR=/workspace/codex-lb/openspec/changes/archive/2026-10-07-repair-five-quota-presentation-contracts/evidence \
node node_modules/@playwright/test/cli.js test --config browser-smoke/quota-contracts.config.ts
```

Ruff lint/format passed on all 13 changed Python files; scoped ty passed on all six changed application modules. Proxy architecture, cancellation safety, timing seams, settings tiers **98/98**, single-head migration topology against local `origin/main`, and simplicity budgets passed. TypeScript, production frontend build and scoped ESLint passed. Strict MkDocs build passed with the locked docs dependency group. CI-pinned OpenSpec 1.11.0 strict validation passed **68/68** main specs and this two-capability change; normative deltas are synced to the main specs and stable context/docs are updated.

Before publication on the rebased tree, the same Python selection was repeated: **884 passed, 4 skipped**. Strict validation again passed all **68 main specs**. The other **333 registry rows** retained the snapshot hash; the upstream firewall test/spec files match the fetched main exactly.

## Boundaries and registry preservation

Only the five selected source rows are closed locally. The other **333 rows** must retain the recorded SHA-256 hash of their exact text. The queue becomes **338 records — 95 local closures, 7 partial, 236 unverified**. The prior external/partial records and F-045, CI-04 and F-082 retain their statuses.

The full repository suite, PostgreSQL/MySQL lock behavior, live Edu/Team quota observations, provider entitlement, cloud CI and public/production artifacts are separate scopes and were not verified here. Upstream state and tests on this source tree do not prove a deployed fix.
