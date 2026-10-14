## ADDED Requirements

### Requirement: Dashboard TOTP accepts password-manager input

The dashboard login TOTP field SHALL expose one-time-code autocomplete, a numeric
input mode and a stable accessible label and name. A six-digit replacement input
event SHALL populate the field and submit verification once without requiring a
clipboard paste. Outside pointer or focus interaction SHALL NOT cancel login.

#### Scenario: Password manager replaces the input value

- **WHEN** a password manager delivers six ASCII digits through a replacement input event
- **THEN** the dashboard submits exactly one verification request containing those digits
- **AND** an outside interaction does not log out the pending session

### Requirement: Fullscreen account controls announce the available action

The dashboard account fullscreen toggle SHALL expose a localized accessible name
for entering fullscreen in normal mode and exiting fullscreen in fullscreen mode.
Its pressed state SHALL reflect the active URL-backed fullscreen state.

#### Scenario: Exit fullscreen is discoverable by accessible name

- **WHEN** an operator enables fullscreen accounts
- **THEN** the toggle is pressed and named with the localized exit-fullscreen action
- **AND** activating it removes fullscreen without resetting other dashboard filters

### Requirement: Session lifetime settings explain locality limits

For a configured password-session lifetime above 30 days, the settings view SHALL
explain that long lifetimes require permitted local access, LAN/remote or proxy
access normally receives 12 hours, and changed settings apply to newly issued
sessions while existing cookies retain their original expiry.

#### Scenario: Long LAN session setting has an explicit policy explanation

- **WHEN** an operator enters a session lifetime greater than 720 hours
- **THEN** the settings view explains the locality restriction and 12-hour remote limit
- **AND** it explains that previously issued sessions retain their expiry
