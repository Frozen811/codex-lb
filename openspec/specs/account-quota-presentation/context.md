# Monthly observations

The quota duration is independent of the plan's estimated credit capacity. Team accounts have reported lone primary windows of both 43200 and 43800 minutes. The inclusive 28–32-day band recognizes both without confusing ordinary 300-minute or 10080-minute windows. An explicit zero-duration secondary is a placeholder; an unknown secondary duration is preserved.

For example, a Team window with 43800 minutes and 96 percent used is Monthly 4 percent remaining. Its monthly credit estimates remain null when no capacity is known. Newer ordinary short or weekly samples supersede older monthly history for plans without monthly capacity, preserving paid-plan upgrades. Existing history is retained; subsequent ordinary refreshes normalize new samples.

Historical rows in the primary slot use the same inclusive duration band and secondary-placeholder rule as ingestion, for every plan. An unknown or positive secondary duration preserves both original windows. A duration outside the band remains primary. Team monthly capacity has no default estimate: its weekly estimate cannot establish monthly credits, while an explicit measured monthly override remains supported.

See [the requirements](spec.md) and [the #1367 change](../../changes/archive/2026-09-10-fix-observed-monthly-quota/context.md) for reproduction and verification evidence.
