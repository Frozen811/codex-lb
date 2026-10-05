## Why

The auth import dialog silently selects only one file. Four additional open registry records need independent verification of their shipped plan, telemetry, WebSocket framing and accessibility contracts.

## What Changes

- Import selected auth files sequentially through the existing authorized API, retain the failed and unattempted suffix, and guard dismissal during the batch.
- Verify Prolite alias import and usage persistence without identity or credential drift (UP-ISSUE-2511).
- Verify interactive CLI traffic is counted in the canonical telemetry family through persisted request logs (UP-PR-2517).
- Verify complete multi-line WebSocket objects reach the HTTP bridge promptly with valid downstream SSE (UP-PR-2519).
- Verify translated capability names and keyboard toggles in both create and edit Model Source forms (UP-ISSUE-2302).

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `frontend-architecture`: ordered multi-file import and named keyboard-operable Model Source capability controls.

## Impact

Import dialog, three existing locales, Accounts flow and Model Source form tests, targeted Python verification, and registry evidence. No API, migration, configuration, credential format or dependency changes. Exactly five selected source records, including UP-PR-2564; broader PR 2065 remains separate.
