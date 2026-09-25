# sticky-session-operations Specification

## Requirements

### Requirement: Sticky sessions are explicitly typed

The system SHALL persist each sticky-session mapping with an explicit kind so durable Codex backend affinity, durable dashboard sticky-thread routing, and bounded prompt-cache affinity can be managed independently. Budget-pressure reallocation MUST apply only to mappings whose kind/source is soft. A raw or legacy `codex_session` mapping MUST remain owner-bound because it may represent explicit turn-state continuity; budget pressure MUST NOT delete or rebind it.

When candidate selection narrows the pool to a single resolved hard continuity owner, a transient error backoff on that owner MUST NOT cause selection to fail or abandon the owner. The selector MUST admit the sole candidate under backoff fallback while preserving the owner's error counters. Persisted unavailability (`PAUSED`, `DEACTIVATED`, `RATE_LIMITED`, `QUOTA_EXCEEDED`, expired reauth) MUST continue to fail closed.

#### Scenario: Hard continuity owner in transient error backoff is admitted
- **GIVEN** a request with a resolved hard continuity owner
- **AND** the owner account is `ACTIVE`
- **AND** the owner account has accumulated transient errors placing it into bounded error backoff
- **WHEN** selection evaluates the candidate pool narrowed to the owner
- **THEN** selection admits the owner account via backoff fallback
- **AND** the request does not fail as `hard_affinity_saturated` or `continuity_owner_unavailable`
- **AND** the owner's error counters remain intact

#### Scenario: Hard continuity owner with persisted unavailability fails closed
- **GIVEN** a request with a resolved hard continuity owner
- **AND** the owner account is `PAUSED`, `DEACTIVATED`, `RATE_LIMITED`, or `QUOTA_EXCEEDED`
- **WHEN** selection evaluates the candidate pool narrowed to the owner
- **THEN** selection returns no account and fails closed
