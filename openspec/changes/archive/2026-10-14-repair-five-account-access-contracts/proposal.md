## Why

Exactly five unverified registry rows are selected: UP-ISSUE-1132, UP-DISC-636, UP-DISC-1593, UP-ISSUE-1919 and UP-DISC-884. Access-token-only exports fail frontend validation, and exporting explicit account identity loses metadata needed to import that identity again. Long account identifiers also need browser verification.

## What Changes

- Preserve explicit import identity in Codex-format auth exports and accept absent optional credentials in the frontend.
- Keep absent credentials absent in downloads and omit their copy controls.
- Bound account/export identity text within the viewport.
- Independently verify Business sibling identity isolation, Guardian keepalive and API-key model sources; document their local and provider boundaries.
- Update exactly five registry rows with saved evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-auth-export`: nullable credential rendering and explicit identity round-trip.
- `frontend-architecture`: account/export identity overflow containment.

## Impact

Backend accounts schemas/service; frontend accounts schemas/export dialog; focused backend/frontend/browser regressions; OpenSpec/context and registry. No migration, runtime setting, publication or deployment.
