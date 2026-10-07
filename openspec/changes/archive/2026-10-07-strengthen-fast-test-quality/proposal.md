## Why

Parallel CI preserves suite selection, but broad timing windows and eventual
layout assertions need precise regression checks. Deeper generated coverage
should supplement the fast mandatory pipeline without extending its critical path.

## What Changes

- Add virtual-time startup boundary and cancellation regressions.
- Check rendered dashboard resize frames and settled geometry without retries.
- Clip transient stale sparkline widths to their responsive containers, fixing
  the document overflow exposed by the stronger frame check.
- Exercise concurrent reservation admission, settlement and release in one real
  database with separate sessions and explicit synchronization.
- Keep normal property-test budgets and add pinned edge examples; run selected
  properties with at least 500 examples in a seeded, scheduled/manual workflow.
- Preserve existing required CI suites and measure cloud runtime against 6m20s.

## Impact

Tests, GitHub automation, contributor instructions and responsive sparkline
containment change. Production timing, database semantics and existing required
check names do not.
