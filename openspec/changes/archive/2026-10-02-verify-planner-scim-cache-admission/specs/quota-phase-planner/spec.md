## MODIFIED Requirements

### Requirement: Working-hour updates contain valid clock times

The quota planner settings API MUST reject supplied working-hour times unless
they use ASCII `HH:MM` format with hours from 00 through 23 and minutes from
00 through 59. An invalid update MUST NOT persist any accompanying changes.
Omitted or null times MUST retain their existing values. Reading legacy
settings MUST remain possible, and the existing scheduler fallback for legacy
malformed times MUST remain available. Legacy clock strings outside `HH:MM`
MUST be returned unchanged so operators can correct them; a partial update
MUST NOT require correcting the other legacy clock string first.

#### Scenario: Impossible clock time does not change settings

- **WHEN** an operator supplies `99:99`, `24:00`, or `12:60` with another setting
- **THEN** the API returns a validation error and no setting changes

#### Scenario: Boundary clock times are accepted

- **WHEN** an operator supplies `00:00` and `23:59`
- **THEN** both values are saved and returned unchanged

#### Scenario: Legacy malformed times remain visible and correctable

- **GIVEN** historical settings contain clock strings such as `9:00` or `bad`
- **WHEN** an operator reads settings, computes a forecast, or corrects one clock field
- **THEN** each request completes successfully using the existing scheduler fallback where needed
- **AND** the uncorrected stored field remains unchanged and readable
