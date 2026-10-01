## ADDED Requirements

### Requirement: Direct WebSocket dispatch respects routing-unavailable accounts

For `/v1/responses` and `/backend-api/codex/responses` direct WebSockets, the proxy MUST check the selected account's routing-unavailable state immediately before sending each new `response.create`, including on an already-open socket and after asynchronous admission waits. Once an operator Pause has been committed and its routing-unavailable mark is visible on the serving replica, the proxy MUST NOT send that turn through the paused account.

A refused unsent turn MUST receive a terminal server error and release its API-key reservation and response-create admission without recording account-health failure or rerouting account-owned payloads. Anchored turns MUST use `previous_response_owner_unavailable`; unanchored turns MUST use `upstream_unavailable`. Refusing a new turn MUST NOT close a shared socket or cancel unrelated already-dispatched responses. The existing cross-replica convergence bound SHALL continue to apply.

#### Scenario: Pause between turns blocks reuse

- **GIVEN** a direct WebSocket has completed a response on account A
- **WHEN** an operator pauses A and the local routing-unavailable mark is visible before another response.create
- **THEN** the second turn receives a terminal error and no second response.create is sent upstream
- **AND** the first response's ownership remains unchanged

#### Scenario: Pause during admission blocks unsent work

- **GIVEN** a response.create has selected account A and is waiting on asynchronous admission
- **WHEN** A becomes routing-unavailable before the final send boundary
- **THEN** the turn is refused and its admission and reservation are released without upstream dispatch

#### Scenario: Pause does not cancel unrelated dispatched responses

- **GIVEN** a direct WebSocket still carries an already-dispatched response on account A
- **WHEN** A is paused and a second turn is refused
- **THEN** the already-dispatched response can still complete on its existing socket
- **AND** only the new unsent turn is refused
