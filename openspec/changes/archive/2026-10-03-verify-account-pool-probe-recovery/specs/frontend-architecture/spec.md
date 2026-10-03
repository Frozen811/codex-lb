## ADDED Requirements

### Requirement: Quota-exceeded accounts expose manual Resume

The Accounts detail actions MUST expose Resume for `quota_exceeded` accounts through the existing account-reactivation action. Resume MUST be disabled while an operation is busy or the view is read-only. Reauthentication-required accounts MUST NOT expose Resume. Existing paused and deactivated Resume actions MUST remain available under their existing restrictions.

#### Scenario: Operator resumes a quota-exceeded account

- **GIVEN** a selected quota-exceeded account in a writable view without a busy operation
- **WHEN** the operator invokes Resume
- **THEN** the existing reactivation action receives that account's identifier exactly once

#### Scenario: Busy and read-only views protect Resume

- **GIVEN** a selected quota-exceeded account
- **WHEN** the view is read-only or an operation is busy
- **THEN** Resume is disabled and does not invoke reactivation

#### Scenario: Reauthentication remains mandatory

- **GIVEN** a selected reauthentication-required account
- **WHEN** account actions are displayed
- **THEN** reauthentication remains available and Resume is absent
