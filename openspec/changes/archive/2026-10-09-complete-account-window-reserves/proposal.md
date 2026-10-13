## Why

UP-PR-1528 remains partial after scalar-cap repair. Complete its account reserve policy, per-window overrides, current-owner admission fences and faithful dashboard reserve accounting while retaining four already-verified tasks.

## What Changes

- Adapt the current published account reserve implementation and tests from upstream PR #1528 at caf31b77a4ef85047459635e956fdd62f7fbd7ce.
- Add the disabled-by-default shared policy, optional 5-hour/weekly overrides, atomic disable/remove and fresh data gating.
- Enforce policy at ordinary/sticky/bridge/WebSocket and synthetic warm-up selection and final dispatch, retaining settled owner/cleanup paths.
- Show provider remaining, reserved and usable quota and retain provider-scale weekly burn.
- Add one forward migration on the local warm-up revision, preserving existing scalar caps and other dirty repairs; retain legacy API compatibility.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `account-routing`: account reserve policy and current-owner dispatch fences.
- `proxy-warmup`: reserve-aware synthetic warm-up.
- `quota-phase-planner`: reserve-aware planner authorization and settlement.
- `database-migrations`: forward reserve migration on current fork graph and legacy scalar compatibility.

## Impact

Only remaining UP-PR-1528 of the original exact-five selection. Reuse upstream account/usage/proxy/frontend changes selectively; omit upstream CI/dependency and historical migration changes. Keep own restore, reset-credit and warm-up fixes. No branch, commit, push or deployment. Attribution: NikitaMGrimm and aaravrav via the published upstream PR.
