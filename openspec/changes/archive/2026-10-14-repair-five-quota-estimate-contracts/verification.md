# Verification: five quota-estimate contracts

2026-10-14, Europe/Kiev. Initial HEAD `cfc939cc69e6534996365a348b74eaf414283f34`,
branch main. Exactly five initially НЕ ПРОВЕРЕНО records were selected. The
initial 126 dirty files were hashed before edits. This is local verification;
there is no fixing commit or new hosted CI, publication or deployment evidence.

## Results by selected record

| Record | Result |
| --- | --- |
| UP-ISSUE-2420 | Fixed locally: independent weekly Pro Lite/Pro estimates 9000/36000 replace 37800/50400. Full Lite plus exhausted Pro now yields 45000 estimated capacity, 9000 remaining and 20% pooled remaining through the actual dashboard API. Short-window estimates and observed percentages/reset times are preserved. These community estimates are explicitly identified as estimates, not calibrated provider entitlements. |
| UP-ISSUE-2557 | Fixed locally: non-finite and boolean overrides are rejected; per-window overrides remain independent; the next pace response resolves the Pro reference dynamically. Both frontend numeric constants were removed. API metadata and the card identify estimated credits. Zero/missing references suppress equivalents. The existing override hook is process-local and programmatic, not a new persisted operator UI/API. |
| UP-ISSUE-1793 | Fixed locally: current-window USD equivalents are per account and use matched `(first sample, last sample]` cost intervals and increasing percent observations in one reset epoch. Overview 1d/30d and projections return identical 40/120 USD account estimates despite unrelated spend. Legacy pooled fields remain null. Unknown prices and invalid/stale/reset/decreasing observations suppress estimates. UI handles 101 rows with bounded scrolling. A historical time-series/diagnostics view is not introduced. |
| UP-DISC-1551 | Existing current pricing independently verified and locally closed: current/dated Luna identifiers, cached input, ordinary and long-context rates, and reasoning counted once pass. Eight real ASGI POST cases cover `/backend-api/codex/responses`, `/v1/responses` and both trailing-slash aliases, then inspect actual request-log costs. Standard example is 1.222 USD; long-context example is 2.02 USD. No price or historical non-null cost rewrite was needed. |
| UP-DISC-864 | Existing duration semantics independently verified and locally closed: seven Free accounts with observed 30-day windows stay monthly; they do not inflate the Plus weekly summary or runway. This fixes the local explanation/evidence gap, not a claim about comparative live subscription value. |

## Final validation

**868 distinct final test cases passed; one explicit platform skip.** Earlier and
repeated executions are not added to this count.

- Backend quota/dashboard/pricing selection: **295 passed, 1 skipped**, 59.31s.
  `uv run pytest -q tests/unit/test_usage.py tests/unit/test_account_mappers.py
  tests/unit/test_dashboard_weekly_pace.py tests/unit/test_dashboard_projection_history_cap.py
  tests/unit/test_pricing.py tests/unit/test_pricing_catalog.py
  tests/unit/test_quota_estimate_contracts.py tests/integration/test_usage_api.py
  tests/integration/test_usage_summary.py tests/integration/test_dashboard_overview.py
  tests/integration/test_quota_estimate_contracts.py --tb=short --show-capture=no
  --maxfail=5 --junitxml=C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/backend-final.xml`.
- Direct routing/client/plan consumers: **439 passed**, 121.76s.
  `uv run pytest -q tests/unit/test_load_balancer.py
  tests/integration/test_codex_usage_api.py tests/integration/test_plan_json_contracts.py
  --tb=short --show-capture=no --maxfail=5
  --junitxml=C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/routing-final.xml`.
- Frontend: **131 passed** in three files: dashboard `utils.test.ts`,
  `schemas.test.ts` and `components/weekly-credits-pace-card.test.tsx`.
  `bun run test` with those paths and JUnit reporter writes `frontend-final.xml`
  in the same evidence directory. Final run: 4.34s.
- Production Chromium: **3 passed**, 6.7s, no retries, using
  `QUOTA_STAGE=after`, `QUOTA_EVIDENCE_DIR` and
  `bun x playwright test --config browser-smoke/quota-estimates.config.ts`.
  Widths 375/768/1440, account identities/amounts, removal of misleading pooled
  dollar text, no horizontal overflow, and 101-row internal scrolling passed.
  Baseline production UI was captured before rebuilding: three before controls
  passed. Screenshots were inspected at mobile and desktop sizes.
- Repository Ruff and format: passed, 1570 Python files at the repository check;
  final additional plan-test edits also pass scoped Ruff/format.
  Scoped dashboard/usage/account-schema `uv run ty check`: passed.
  Scoped ESLint and final `bun run build` (including TypeScript): passed.
- Proxy architecture, cancellation safety, timing seams, settings tiers,
  migration topology, static migration safety and simplicity budgets: passed.
  Existing graph: 276 revisions, one head; no migration added by this package.
  Runtime migration durations were not measured.
- Pinned `@fission-ai/openspec@1.11.0` strict change validation and strict canonical
  validation: passed, **68/68** specs. Normative deltas are synchronized.
  The GitHub event wrapper cannot run standalone without `GITHUB_EVENT_PATH`;
  its first direct invocation raised that KeyError. Exact change validation was
  run directly; the wrapper is not claimed as a passing cloud check.
- Full own source/test/spec diff reviewed; `git diff --check` passed.

The Windows-only skip is
`test_dashboard_overview.py::test_weekly_credit_pace_timing_treats_naive_reset_as_utc`
because this host lacks `time.tzset`. The actual naive/aware reset interaction in
the new API path is exercised on Windows. Existing Starlette/AnyIO deprecation,
Vite's SWC recommendation and Playwright color-environment warnings were observed.
This is not a warning-free or full-repository pytest claim.

## Regression history and limits

Pre-fix API tests reproduced 88200 instead of 45000 mixed capacity, a spurious
4699.33 USD fleet extrapolation and absent dynamic Pro metadata; invalid-capacity
tests reproduced accepted NaN/infinity/bool. Initial test-harness mistakes used
the pricing function's arguments in the wrong order and expected a short-context
rate for a million-token long-context request; both were corrected. The initial
Free assertion used a nonexistent `monthlyUsage` field and was corrected to the
actual `usage.monthlyRemainingPercent` contract. These were not product defects.

Intermediate existing suites failed on old Pro/Lite numeric expectations and on
the obsolete fleet-dollar behavior. Their expectations now describe the changed
contract; all final selections above pass. Existing exclusions and guard tests
were retained. No skips were introduced to hide a regression.

Source observations: [quota estimates](https://github.com/Soju06/codex-lb/issues/2420),
[independent capacities](https://github.com/Soju06/codex-lb/issues/2557),
[per-account dollars](https://github.com/Soju06/codex-lb/issues/1793),
[Luna pricing](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[announced price reduction](https://openai.com/index/advancing-the-price-performance-frontier-with-gpt-5-6/),
[Free duration discussion](https://github.com/Soju06/codex-lb/discussions/864).
Live provider quota calibration/billing, external unrecorded usage, historical
non-null price correction, server PostgreSQL/MySQL runtime and production are
not established. Capacity-based mixed-plan routing weights deliberately change.

## Evidence and preservation

Raw JUnit and six before/after PNGs are in
`C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/`.
Screenshots: [mobile before](C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/before-375.png),
[mobile after](C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/after-375.png),
[desktop before](C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/before-1440.png),
[desktop after](C:/Users/ext/AppData/Local/Temp/codex-lb-five-quota-20261014/after-1440.png).
These local temporary artifacts are not release assets or a hosted attachment.

Saved-row readback, exact five-row boundary and unrelated dirty-file preservation
are recorded in [closure.json](closure.json). All other 354 source rows remain
unchanged; 120 unrelated initial dirty files retain their SHA256 hashes. Existing
partials, F-045 and CI-04 remain unchanged. No commit/push/PR/merge/release/deploy.
