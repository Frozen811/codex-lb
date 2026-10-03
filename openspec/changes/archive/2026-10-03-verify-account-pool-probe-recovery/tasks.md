## 1. Metrics availability (UP-PR-2523)

- [x] 1.1 Reproduce proven-rejected credentials counted as available through real ASGI metrics exposition and committed account rows.
- [x] 1.2 Pass the committed rejection reason to the shared eligibility predicate and verify status counts, expiry, quiet-pool refresh, failure/recovery, and multiprocess regression tests.

## 2. Force Probe settlement (UP-PR-2524)

- [x] 2.1 Verify weekly-only and expired legacy rows through the dashboard probe route, real rollback/close, and local health recovery without changing response fields.
- [x] 2.2 Verify fresh failures and rejected probes retain health fences using real sessions and existing concurrency regressions.

## 3. Weekly-only recovery (UP-PR-2527)

- [x] 3.1 Verify post-block weekly-primary recovery through the Responses route and committed status readback; retain missing/stale/exhausted evidence and minimum debounce protections.
- [x] 3.2 Verify independent rate-limit holds, local cooldown expiry, unchanged weekly storage, and sticky ownership using route regressions.
- [x] 3.3 Restore dashboard Resume for quota-exceeded accounts; verify callback, busy/read-only restrictions, reauthentication exclusion, backend state transition, and before/after browser screenshots.

## 4. Delivery evidence

- [x] 4.1 Synchronize main observability spec/context and metric scope documentation; pass focused tests, Ruff, typing, applicable repository guards, and strict OpenSpec validation.
- [x] 4.2 Review final changes against requirements, record verification/residuals, update exactly three registry entries and the summary, then archive the verified change.
