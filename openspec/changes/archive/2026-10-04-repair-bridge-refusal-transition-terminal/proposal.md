## Why

Three unchecked registry items concern HTTP bridge continuity and terminal delivery: UP-ISSUE-2389, UP-ISSUE-2388, and UP-ISSUE-2033. Single-turn mocks do not establish alias convergence, and a local timeout refusal can be mistaken for a native transport ending.

## What Changes

- Verify model-transition recovery with durable aliases and a subsequent turn; repair any recurrence while preserving ownership fences.
- Audit transport-coded local refusal sites and attach local provenance only where dispatch has not occurred.
- Verify first-event, later-event, and raised-error health failures through Responses routes with real reservation settlement.
- Record focused evidence and update exactly the selected registry rows.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: define the safe local-refusal class, convergent model-transition alias behavior, and retain the existing single-terminal health contract.

## Impact

HTTP bridge request submission, model-transition streaming and durable alias registration; Responses route regressions; owning OpenSpec spec/context and issues-check.md. No new configuration, migration, release, or deployment.
