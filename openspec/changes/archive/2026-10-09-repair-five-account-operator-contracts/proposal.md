## Why

Five unverified registry tasks expose gaps in account restore, operator quota admission, reset-credit batch ownership and reset-confirmed warm-up. Paused credit observation already exists and needs current API evidence for its observation/redemption boundary.

## What Changes

- Restore explicit backup metadata against the account identity returned by import, including cleared alias, disabled warm-up and paused status.
- Apply account quota caps before error-backoff fallback and independently of standard upstream quota bypass.
- Replace bulk redemption's fabricated/stale remaining-credit snapshots with authoritative account-bound observations.
- Restore the inclusive pre-reset usage threshold, default zero, using a new active database column while preserving the legacy column and historical revisions.
- Verify paused credit observation, cached presentation, polling exclusion and redemption rejection.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-auth-export`: portable restore metadata targets the imported identity.
- `account-routing`: operator quota caps constrain admission and fallback.
- `rate-limit-reset-credits`: bulk redemption requires real credit identities; paused observation remains independent.
- `usage-refresh-policy`: reset warm-up honors the inclusive pre-reset threshold with zero as the default.

## Impact

Exactly UP-ISSUE-850, UP-PR-1528, UP-PR-2497, UP-PR-2122 and UP-ISSUE-2514. Account service, balancer selection, reset-credit API, warm-up service, settings model/schemas/defaults, one forward migration, settings dashboard validation and focused tests. No new endpoint, environment setting or dependency. Verification and registry closure are local; upstream policy, live providers and production remain separate.
