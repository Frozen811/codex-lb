# oauth-callback-privacy Specification

## Purpose
The loopback OAuth callback server's default access logger recorded the full request target, exposing temporary authorization codes and anti-CSRF state tokens in log sinks. This capability keeps the callback functional while omitting credential-bearing query text from access logs.
## Requirements
### Requirement: OAuth callback query credentials stay out of logs

The loopback OAuth callback server MUST NOT emit authorization codes, state
tokens, or the raw callback query string through its generic access log. It
MUST preserve callback routing and handler responses when access logging is
suppressed.

#### Scenario: Successful callback omits query credentials

- **GIVEN** the real loopback callback server is running
- **WHEN** a client requests `/auth/callback` with authorization-code and state query values
- **THEN** the callback handler response is returned unchanged
- **AND** neither query value is emitted by the callback access logger under
  text or JSON logging configuration

#### Scenario: Access suppression is callback-local

- **WHEN** the loopback OAuth callback server suppresses its access record
- **THEN** global application and proxy access-logging configuration remains unchanged

### Requirement: Failed callback listener startup releases resources and preserves manual recovery

An OAuth callback listener whose startup fails or is cancelled MUST release resources acquired by that startup before propagating the failure or cancellation. An occupied callback port MUST retain the existing pending browser flow's manual-callback recovery path and MUST emit a warning identifying the bind host, port and exception type without code, verifier, state, authorization URL or callback query values.

#### Scenario: Callback port is already occupied

- **WHEN** a browser OAuth flow cannot bind its callback port
- **THEN** initialized listener resources are released
- **AND** the flow remains usable for manual callback with a safe warning

#### Scenario: Listener startup is cancelled

- **WHEN** callback listener startup is cancelled after resource initialization
- **THEN** acquired listener resources are released and cancellation propagates

