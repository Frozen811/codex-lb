## Why

Exactly five unverified records concern quota estimates and pricing: UP-ISSUE-2420,
UP-ISSUE-2557, UP-ISSUE-1793, UP-DISC-1551 and UP-DISC-864. Weekly Pro/Lite
capacities misweight mixed pools, duplicated Pro constants ignore overrides, and
the weekly USD headline divides an arbitrary dashboard timeframe's fleet spend
by a different set of account quota observations.

## What Changes

- Use independently specified empirical weekly estimates for Pro and Pro Lite;
  identify absolute credits as estimates and reject non-finite overrides.
- Resolve Pro reference capacity at request time and pass it to the dashboard.
- Estimate full weekly USD value per account from matched quota/cost intervals,
  independently of the dashboard's activity timeframe; retain legacy fields as null.
- Verify current Luna pricing and monthly-only Free aggregation at public paths.
- Update exactly the five selected registry rows with local evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-quota-presentation`: explicit estimates and independent weekly values.
- `frontend-architecture`: per-account weekly USD and API-owned Pro reference.

## Impact

Planned runtime paths: app/core/usage/__init__.py;
app/modules/accounts/schemas.py; app/modules/usage/schemas.py;
app/modules/dashboard/{repository,service,schemas,weekly_pace,weekly_cost}.py;
frontend/src/features/dashboard/{schemas,utils}.ts;
frontend/src/features/dashboard/components/weekly-credits-pace-card.tsx and
frontend/src/i18n/locales/{en,ko,zh-CN}.json. Focused unit/integration/component
coverage, canonical specs/context and issues-check.md accompany these edits.
No migration, dependency, environment setting or publication is required.
