## ADDED Requirements

### Requirement: Direct WebSocket terminal evidence preservation

A direct WebSocket frame-less ending (`None` or synthetic 1006) MUST remain account-neutral only for close-kind messages or error-kind messages with positive transport-ending provenance. Protocol-invalid messages and authored non-clean closes MUST retain account penalties. An unsafe-to-migrate selected-owner terminal MUST preserve its sanitized upstream error and supported metadata, settle once and MUST NOT become a pre-dispatch owner-unavailable error.

#### Scenario: Direct or routed frame-less receive failure

- **WHEN** a dispatched direct WebSocket request ends with positive transport-ending evidence and no authored close frame
- **THEN** the request fails without a per-drop account penalty or replay
- **AND** visible or sequenced progress does not change health attribution

#### Scenario: Protocol failure has no ending provenance

- **WHEN** an error-kind protocol-invalid message carries no authored close frame and no transport-ending evidence
- **THEN** it retains the account penalty
- **AND** a missing close code alone does not establish transport-ending provenance

#### Scenario: Selected owner returns an authentic quota terminal

- **WHEN** an already-dispatched anchored request receives a quota terminal and migration is unsafe
- **THEN** its sanitized status, type, code, message, parameter and supported retry metadata survive
- **AND** no cross-account dispatch occurs and settlement and health bookkeeping run once
