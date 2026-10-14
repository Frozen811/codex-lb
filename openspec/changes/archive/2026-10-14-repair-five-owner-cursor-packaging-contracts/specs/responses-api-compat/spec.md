## ADDED Requirements

### Requirement: Required-owner WebSocket connect errors retain their original envelope

Before response dispatch, a WebSocket connection failure on a required response, file or session account owner MUST preserve the upstream status, error code and message. The connect loop MUST NOT exclude that owner and reselect into a generated owner-unavailable error. Movable requests MUST retain their existing eligible-account failover. Failed attempts MUST release their account stream lease and retain API-key settlement ownership. The equivalent HTTP bridge path MUST preserve the original connect failure.

#### Scenario: A required owner rejects a connection
- **WHEN** a required owner rejects WebSocket connection with a retryable HTTP 403 or 429
- **THEN** the client receives the original status, error code and message
- **AND** no replacement account is attempted and the failed stream lease is released

#### Scenario: An unbound request can move
- **WHEN** an unbound request receives an account-scoped retryable connection failure and an eligible replacement exists
- **THEN** the connect loop can select that replacement under its existing attempt budget

#### Scenario: An owner-bound HTTP bridge connection fails
- **WHEN** an HTTP Responses continuation cannot establish its required owner's upstream WebSocket
- **THEN** its external error envelope retains the original account-scoped failure
