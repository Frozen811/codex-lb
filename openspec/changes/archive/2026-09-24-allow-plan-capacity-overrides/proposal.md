# Proposal: Allow Plan Capacity Overrides

## Summary

Support registering plan credit capacity overrides for supported account plans and windows (`primary`, `secondary`, `monthly`). This allows operators to calibrate hard-coded plan capacities (such as Pro and Pro Lite in mixed pools, issue #2420) to match observed token consumption without violating simplicity budgets or modifying source code constants.

## Motivation

Issue #2420 observed that hard-coded credit capacities for Pro and Pro Lite accounts disagree with observed quota exhaustion cycles in mixed pools, causing the dashboard remaining credit display and weekly pace projections to distort available capacity. Hard-coded values (`37800.0` for `prolite` and `50400.0` for `pro`) cannot be calibrated to reflect actual token burn in specific deployment scenarios. Providing an explicit override mechanism enables exact pool calibration while preserving default values for unconfigured plans.

## Proposed Changes

- Add in-memory capacity override registry functions to `app/core/usage/__init__.py`:
  - `set_plan_capacity_override(plan_type, window, capacity)`
  - `clear_plan_capacity_overrides()`
  - `get_plan_capacity_overrides()`
- Update `capacity_for_plan(plan_type, window)` to check registered overrides before falling back to default dictionaries.
- Add regression unit tests proving overrides take precedence and clear cleanly.

## Capabilities

### Modified Capabilities
- `usage-refresh-policy`: Added requirement for plan capacity overrides taking precedence in `capacity_for_plan`.
