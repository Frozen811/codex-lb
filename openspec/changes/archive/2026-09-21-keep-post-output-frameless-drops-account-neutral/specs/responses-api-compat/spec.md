## MODIFIED Requirements

### Requirement: Abrupt upstream websocket drops remain account-neutral

When an HTTP bridge upstream websocket ends with a terminal transport message (a close or receive error) that carries no upstream-authored close frame (`None` or adapter-synthesized RFC 6455 `1006`) and no established account-neutral transport classification (process-network, liveness-timeout, keepalive-timeout), the proxy MUST NOT write per-drop account error-health (`record_error`) for that unclassified `stream_incomplete` drop, regardless of whether application-layer output or response events were already observed. When such a drop occurs before any application-layer output was observed (zero response events and no buffered reasoning prelude) and settles its pending requests as failures, the proxy MUST record it into the windowed eventless account failure signal so that repeated eventless drops on the same account within the window still apply the drain penalty. Drops occurring after application-layer output was observed MUST NOT be recorded into the eventless failure signal. A failure that carries an upstream-authored close frame (including non-clean codes such as 1008 or 1011) or arrives as a non-terminal protocol-invalid frame (for example a binary message) MUST keep the existing account penalty semantics. The per-bridge retry circuit MUST still record the failure at bridge scope.

#### Scenario: Sporadic frame-less drops do not strand a continuity-bound conversation

- **GIVEN** a conversation continuity-bound to account A via `previous_response_id`
- **AND** account A's upstream websocket drops three times with no close frame and zero response events, spread wider than the eventless failure window
- **WHEN** the client sends the next continuity-bound follow-up
- **THEN** account A's `error_count` receives no per-drop increment and stays below the error-backoff threshold
- **AND** the follow-up still routes to account A instead of failing with `previous_response_owner_unavailable`

#### Scenario: Post-output frame-less drops do not penalize account health

- **GIVEN** an active request that has received response events or buffered model output on account A
- **WHEN** the upstream websocket terminates abruptly with no close frame (`None` or 1006)
- **THEN** account A's `error_count` receives no per-drop increment and the account is not penalized
- **AND** the drop is not recorded into the windowed eventless failure signal
- **AND** the interrupted request fails closed to the client

#### Scenario: Repeated eventless drops inside the window still drain the account

- **GIVEN** an account whose upstream websocket drops with no close frame and zero response events on three separate bridge failures within the eventless failure window
- **WHEN** the third drop is recorded
- **THEN** the windowed eventless failure signal applies the minimum drain penalty so new turns avoid the account until its health probe succeeds

#### Scenario: Close frames keep the account penalty

- **GIVEN** an upstream websocket ending that carries an upstream-authored close frame (for example 1008 or 1011), or a non-terminal protocol-invalid binary frame
- **WHEN** the reader failure path settles the pending requests
- **THEN** the account penalty semantics are unchanged from before this change
