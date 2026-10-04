## Why

UP-ISSUE-2273, UP-ISSUE-2272 and UP-ISSUE-2271 remain unchecked in the local registry. Incomplete accounting and cooldown loading have source fixes, but claim cancellation can lose a committed receipt and claim cleanup can erase a replacement's local probe.

## What Changes

- Verify incomplete reason accounting through actual bridge terminals and durable state.
- Verify absent/elapsed cooldown admission and active local probe preservation.
- Defer cancellation until bounded claim acquisition returns, attach ownership before propagating cancellation, and return only an undispatched request's claim.
- Preserve replacement local probes during durable claim release.
- Record local evidence and retain owner-crash/expiry policy and non-SQLite runtime residuals for UP-ISSUE-2271.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: bridge retry accounting, cooldown admission and cancellation-safe claim ownership.

## Impact

HTTP bridge retry circuit and request submission, focused unit/integration tests, responses spec/context and exactly three source-queue rows. No settings, dependencies, schema changes or publication.
