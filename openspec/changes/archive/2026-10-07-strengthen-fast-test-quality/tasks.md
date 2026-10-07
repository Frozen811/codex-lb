## Implementation

- [x] Add startup boundary, late-error and cancellation tests using virtual time.
- [x] Check dashboard containment during resize and after layout readiness.
- [x] Add synchronized real-database reservation race regressions.
- [x] Add explicit generated-test edge cases and a reproducible extended workflow.
- [x] Update workflow contracts and canonical specification/context.

## Verification

- [x] Run focused tests, property profiles, browser smoke, lint and strict specs.
- [x] Verify unchanged shard completeness and normal generated-test budgets.
- [x] Pass all 1746 Vitest tests without concurrent local loads or timeout changes.

## Publication follow-up

After publishing the verified implementation to main, run full GitHub CI and
manually dispatch the extended properties. Save conclusions, job/workflow
timestamps and the comparison with 6m20s in the ignored
`.test-results/quality-20261007/` evidence report.
