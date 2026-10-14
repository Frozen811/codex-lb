## Decisions

Weekly Pro Lite/Pro estimates become 9000/36000 based on the completed-cycle
observations in #2420. They are estimates, not upstream entitlements. Short-window
values and other plan estimates remain unchanged. Explicit overrides are per plan
and window and must be finite and nonnegative. Routing continues to use the same
central capacity lookup.

The weekly pace response carries the current Pro reference capacity; consumers
must not embed another numeric reference. Legacy frontend-only forecasts omit
Pro-account equivalents when this metadata is absent.

USD estimates use a single account's monotonic quota samples within one reset
epoch and costs attributed to the same observation interval. They never combine
accounts, plans, unrelated dashboard timeframes, or reset epochs. Missing prices,
insufficient samples and zero quota changes produce no dollar estimate. Queries
are sequential and bounded in batches on the request's own AsyncSession.

The existing fleet USD fields remain nullable for wire compatibility and are no
longer populated. UI shows an explicit per-account estimate and estimated-credit
explanation. Existing subscription percentages/reset times remain authoritative.

## Verification boundaries

Synthetic SQLite/ASGI and frontend browser tests establish local behavior only.
No live quota calibration, upstream billing validation, cloud CI, release or
deployment is claimed. Current prices can be validated independently from
historical non-null request costs, which are never rewritten by this change.
