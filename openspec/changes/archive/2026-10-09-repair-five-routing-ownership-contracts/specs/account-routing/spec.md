## ADDED Requirements

### Requirement: Exact model-not-found failures remain model-scoped and owner-safe

An exact upstream `model_not_found` code MUST be authoritative model-scoped, account-health-neutral evidence, including HTTP 404. A fresh movable HTTP or pre-created WebSocket request MUST retain its existing bounded opportunity to try eligible sibling accounts before visible output. Independent required owners MUST remain pinned. When replacement is unavailable or exhausted, the original upstream status and error envelope MUST be preserved. Ordinary `invalid_request_error` MUST NOT acquire model-rejection failover solely from its code.

#### Scenario: Movable model rejection tries an eligible sibling

- **WHEN** a fresh movable request receives exact `model_not_found` before acceptance
- **THEN** the proxy can try an eligible sibling within its existing retry bounds without penalizing account health

#### Scenario: Required owner or exhausted replacements preserve the rejection

- **WHEN** the request has a required owner or no legal replacement remains
- **THEN** the original model rejection reaches the client without cross-account owner abandonment or a synthesized owner-unavailable replacement

#### Scenario: Ordinary invalid request is not a model signal

- **WHEN** the upstream error is an ordinary invalid request without authoritative model-rejection evidence
- **THEN** existing non-retryable behavior remains unchanged

### Requirement: Encrypted input rejections do not poison replacement account health

An upstream `invalid_encrypted_content` rejection or recognized reasoning-payload rejection MUST leave the selected account's health untouched when the HTTP status is 400 or no HTTP status is available. It MUST preserve the original surfaced envelope and MUST NOT enable another replay. An otherwise identical non-400 HTTP failure MUST retain its ordinary account-health handling.

#### Scenario: Replacement rejects encrypted input

- **WHEN** a replacement returns HTTP 400 or an error frame rejecting encrypted input
- **THEN** its transient error count, backoff, and persistent availability remain unchanged
- **AND** the upstream rejection reaches the client unchanged

#### Scenario: Non-400 status is not a payload exemption

- **WHEN** an HTTP server failure uses the same code or reasoning-related message
- **THEN** ordinary failure classification and account-health handling remain active

### Requirement: Transient backoff does not empty a hard continuity owner pool

A request with a resolved hard continuity owner MUST retain admission to that active owner during bounded transient error backoff when all other eligibility, exclusion, quota, and concurrency gates permit it. Admission MUST NOT clear the owner's error counters or move the request to a sibling. Persisted unavailability, caller exclusions, and local caps MUST remain enforced, and movable requests MUST continue to prefer healthy eligible siblings.

#### Scenario: Active backed-off owner remains admissible

- **WHEN** the required owner is active and only its transient backoff would empty the narrowed pool
- **THEN** selection returns that owner without clearing its transient health state

#### Scenario: Hard owner exclusion or cap cannot be bypassed

- **WHEN** the required owner is excluded, persistently unavailable, or at its local cap
- **THEN** selection fails closed without choosing a sibling
