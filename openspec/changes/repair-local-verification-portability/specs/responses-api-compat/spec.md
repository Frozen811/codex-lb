## ADDED Requirements

### Requirement: Same-owner WebSocket fresh resends validate async identity

Before constructing a fresh resend for a client-supplied previous-response miss, the direct WebSocket classifier MUST reject nonboolean async markers on function/custom calls and reject asynchronous calls with missing or blank call IDs. A rejected history MUST NOT cause another upstream connection or fresh request dispatch. The existing endpoint-specific upstream-anchor error envelope MUST remain intact. Valid asynchronous histories and existing same-owner account-bound payload policy MUST remain unchanged.

#### Scenario: Blank asynchronous identity cannot authorize resend
- **WHEN** a client full resend contains an asynchronous function/custom call with a missing or whitespace-only call ID and upstream rejects the prior anchor
- **THEN** the proxy emits one failure using the existing endpoint-specific error code and does not reconnect or dispatch a fresh request

#### Scenario: A malformed async marker cannot authorize resend
- **WHEN** a function/custom call uses a string, number or null async marker in client-supplied full history
- **THEN** the fresh-resend classifier fails closed without an additional upstream connection

#### Scenario: A valid async call keeps same-owner recovery
- **WHEN** the verified full history contains a boolean asynchronous call with an exact nonblank ID
- **THEN** the existing bounded same-owner recovery preserves the complete input history and produces one recovered lifecycle
