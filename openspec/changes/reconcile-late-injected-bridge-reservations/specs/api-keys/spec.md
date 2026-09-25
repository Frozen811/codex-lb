# api-keys Specification Delta

## Requirements

### Requirement: Request-aware API-key usage reservations

#### Scenario: Late anchor injection reconciles in-flight reservation

- **GIVEN** an API-key reservation was admitted with a self-contained input budget
- **WHEN** the HTTP bridge advances a durable hard-turn operation or session anchor and injects `previous_response_id` before dispatch
- **THEN** the system MUST reconcile the in-flight reservation against the conservative opaque-context budget before the anchored frame is dispatched
- **AND** if the reconciled reservation exceeds the remaining limit value, the request MUST be refused with a 429 rate limit error prior to dispatch
