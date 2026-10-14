# Quota presentation context

## Absolute credits are estimates

Capacity converts an observed quota percentage into an estimated absolute credit
balance. It is not an upstream credit grant. The fork independently specifies the
weekly Pro Lite/Pro estimates as 9000/36000 using the completed-cycle observations
in [upstream issue 2420](https://github.com/Soju06/codex-lb/issues/2420).
Those observations are community measurements, not verified provider entitlements.
Short-window values and other plans retain their previous, uncalibrated estimates;
weekly values are not recomputed from hours in a week. The caution applies to
all existing absolute estimates, including Plus and Enterprise.

For example, full Pro Lite plus exhausted Pro now has 45000 estimated weekly
credits and 9000 remaining: 20 percent. Measured upstream percentages and reset
times remain unchanged. Capacity-based strategies also consume these estimates,
so the correction deliberately changes relative weights in mixed pools; it is
not a measured improvement in production throughput or guaranteed allowance.

`set_plan_capacity_override(plan, window, capacity)` remains a process-local
programmatic hook. It accepts finite nonnegative values, including zero, applies
to the normalized plan and selected window only, and is cleared at process exit.
It is not a persisted dashboard setting or a cross-replica configuration API.
The weekly pace response resolves Pro's reference through the same lookup on each
request; clients omit Pro equivalents without a positive API-owned reference.
Zero, missing and unknown capacities must not fabricate an entitlement.

Seven Free accounts with observed 30-day windows contribute to the monthly pool,
not the Plus weekly pool. The old numeric comparison in
[discussion 864](https://github.com/Soju06/codex-lb/discussions/864) mixes durations.
These presentation and normalization controls do not establish comparative real
subscription value.

The normative contract is in [spec.md](spec.md). Verification for this correction
is in the archived five-quota-estimate change.

## Monthly observations

The quota duration is independent of the plan's estimated credit capacity. Team accounts have reported lone primary windows of both 43200 and 43800 minutes. The inclusive 28–32-day band recognizes both without confusing ordinary 300-minute or 10080-minute windows. An explicit zero-duration secondary is a placeholder; an unknown secondary duration is preserved.

For example, a Team window with 43800 minutes and 96 percent used is Monthly 4 percent remaining. Its monthly credit estimates remain null when no capacity is known. Newer ordinary short or weekly samples supersede older monthly history for plans without monthly capacity, preserving paid-plan upgrades. Existing history is retained; subsequent ordinary refreshes normalize new samples.

Historical rows in the primary slot use the same inclusive duration band and secondary-placeholder rule as ingestion, for every plan. An unknown or positive secondary duration preserves both original windows. A duration outside the band remains primary. Team monthly capacity has no default estimate: its weekly estimate cannot establish monthly credits, while an explicit measured monthly override remains supported.

See [the requirements](spec.md) and [the #1367 change](../../changes/archive/2026-09-10-fix-observed-monthly-quota/context.md) for reproduction and verification evidence.
