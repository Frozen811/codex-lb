## Why

UP-ISSUE-2483, UP-ISSUE-1901 and UP-ISSUE-2291 remain unchecked in the independent registry despite existing implementation claims. SQLite also interprets negative LIMIT values as unlimited, allowing a malformed projection cap to restore the full-history read.

## What Changes

- Validate capped projection-history inputs and verify indexed newest-row selection, account cutoffs and the uncapped recent floor.
- Independently verify the reports API on a 543,000-row SQLite history, including folded totals and exact short-window speed metrics; replace unmeasured performance claims with evidence.
- Verify bounded, fair transcript backlog passes without interval waits, including real persistence, failures and terminal settlement.
- Close exactly the three selected local registry scopes and preserve external/platform limitations.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `usage-refresh-policy`: capped history reads reject invalid limits and preserve bounded tails and explicit recent floors.
- `report-aggregation`: add a scenario covering a dense seven-day report through the public endpoint.
- `responses-api-compat`: specify fair continuous transcript backlog flushing.

## Impact

`app/modules/usage/repository.py`, new focused tests, selected ISSUES.md claims, issues-check.md and the three owning OpenSpec capabilities. No migration, new configuration or dashboard rendering change. The authorized commit targets Frozen811/codex-lb main; unrelated pre-existing work remains outside that commit.
