## Why

Five unverified registry rows cover dashboard autofill, account containment,
Compact/fullscreen views, telemetry consent and session lifetime. Existing
implementations need product-path verification; failed consent saves are silent
and long-session copy omits the effective remote lifetime policy.

## What Changes

- Verify UP-ISSUE-2418, UP-ISSUE-1946, UP-PR-2464, UP-PR-2377 and UP-DISC-1820 only.
- Surface failed telemetry consent updates while preserving retry and dismissal.
- Keep account actions contained and fullscreen controls accessible in both states.
- Explain the existing long-session locality policy and unchanged issued cookies.
- Add focused component, browser and real authentication API evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `frontend-architecture`: accessible fullscreen exit and session policy disclosure.
- `telemetry`: visible consent-save failures and retry without a persisted decision.

## Impact

Frontend auth/account/dashboard/settings components, three existing locales,
focused regression coverage and issues-check.md. No dependency, migration, new
setting, navigation item or routing change. Prior dirty work is preserved.
