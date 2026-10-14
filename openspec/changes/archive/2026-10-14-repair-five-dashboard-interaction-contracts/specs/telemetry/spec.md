## MODIFIED Requirements

### Requirement: One-time consent dialog with exact payload preview

The dashboard MUST present a one-time consent dialog on first entry while consent is
`undecided`, and the dialog MUST make the exact snapshot envelope the instance would
transmit available behind an initially collapsed disclosure. The dialog MUST show
one short summary of the transmitted categories, excluded identity/content data
and default activation, without placing the envelope before the decision actions.
Preview and sender MUST use one shared envelope constructor. The preview timestamp MUST record preview generation time as a representative current timestamp;
the actual send MUST regenerate that value at transmission time.

A decision (enable or disable) MUST be persisted and the dialog MUST NOT be shown again after
any decision. The dialog MUST offer equally prominent decision actions with no fewer clicks for
disabling than enabling. Dismissal without a decision MUST be remembered per browser,
MUST NOT persist consent, and MUST prevent repeated dialog-preview aggregation for
that browser while the dismissal marker is present.

The consent API MUST build the preview only while the undecided dialog is eligible or when an
operator explicitly requests it for the settings view. The response MUST retain the `preview`
field and set it to `null` when the preview was not requested and is not dialog-relevant.

#### Scenario: Undecided operator sees payload preview

- **WHEN** an operator opens the dashboard while consent is `undecided`
- **THEN** a dialog offers the exact live snapshot JSON in an initially collapsed
  disclosure with equally prominent enable and disable actions

#### Scenario: Decision is final until changed in settings

- **WHEN** the operator chooses disable in the dialog
- **THEN** consent persists as `disabled`, no snapshot is transmitted afterward, and the
  dialog never reappears

#### Scenario: Decided consent status is a cheap read

- **WHEN** the dashboard reads consent after a persisted decision without requesting a preview
- **THEN** the response contains `preview: null` and no snapshot aggregation query runs

#### Scenario: Settings explicitly requests collected data

- **WHEN** the settings view requests a preview for any consent state
- **THEN** the response contains a current snapshot envelope built with the same schema as the sender

## ADDED Requirements

### Requirement: Consent save failures remain visible and retryable

When a telemetry consent update fails, the dialog SHALL display the request error,
remain open, and allow either decision to be retried after the request completes.
A failed update SHALL NOT persist a decision or browser dismissal. The payload
preview SHALL remain collapsed until requested and the actions equally prominent.

#### Scenario: Failed opt-out can be retried

- **WHEN** an operator disables telemetry and the server rejects the update
- **THEN** the dialog displays the error and remains open without recording dismissal
- **AND** a subsequent successful disable persists the decision and closes the dialog
