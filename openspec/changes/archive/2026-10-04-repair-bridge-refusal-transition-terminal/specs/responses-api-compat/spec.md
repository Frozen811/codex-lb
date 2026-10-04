## ADDED Requirements

### Requirement: Proven local HTTP bridge refusals remain actionable for native clients

HTTP Responses ingress MUST deliver a structured error before commitment or exactly one terminal failure after commitment when the bridge locally refuses a request before pending-request publication and upstream dispatch. Retry-circuit suppression, stale-anchor generation refusal, and pre-dispatch session retirement or closure MUST retain local-refusal provenance through signed internal owner forwarding when the request state proves no prior send or response events. Their existing public status, code and retry hint MUST be preserved. Local-refusal provenance MUST NOT independently authorize replay of a continuation over raw HTTP. An already-dispatched request, reconnect transport failure, prewarm failure or failure after upstream response events MUST NOT be reclassified solely from its transport-like error code.

#### Scenario: Native continuation is suppressed before dispatch

- **WHEN** a retry circuit or stale generation refuses an undispatched native continuation
- **THEN** the client receives an actionable failure rather than an empty successful response
- **AND** no additional upstream frame is sent and the reservation is released

#### Scenario: Session closes before dispatch

- **WHEN** a session is retiring, unregistered or closed before a new request is published or sent
- **THEN** the native client receives the local failure and no new frame is sent

#### Scenario: Genuine transport ending retains provenance

- **WHEN** a bridge request has already dispatched and its upstream transport ends
- **THEN** the native transport-ending lifecycle remains in effect

### Requirement: Model-transition recovery publishes guarded successor continuity

An eligible local account-neutral model-transition owner-conflict recovery MUST retain the downstream turn-state token for guarded durable successor registration while clearing parent identity from upstream submission. After successful recovery, the next request with that turn state and the new model MUST resolve to the child without another fork, including when the completed history contains account-owned output. The child MUST exclude the conflicting owner. Registration MUST preserve protected live-parent aliases and fail closed before dispatch when publication is refused.

#### Scenario: Next turn follows a recovered model transition

- **WHEN** an eligible model-transition child completes and a next turn repeats the same turn-state token
- **THEN** durable and live lookup resolve to the successor and no further model-transition fork occurs

#### Scenario: Protected parent cannot be stolen

- **WHEN** recovery attempts to register a token still owned by a protected live parent
- **THEN** the child is refused before dispatch and the parent token retains its owner

### Requirement: Post-terminal health failures preserve stream completion

After publishing a terminal Responses event, the proxy MUST log ordinary failures from subsequent account-error health writes without emitting another terminal event or aborting stream completion. This MUST apply to first-event, later-event, and raised upstream errors, with and without an API-key reservation. Required reservation settlement MUST precede the health write. Cancellation MUST retain its existing propagation and cleanup behavior.

#### Scenario: Account health persistence fails after a terminal response

- **WHEN** an upstream failure produces a terminal response and the subsequent account-error health write raises an ordinary exception
- **THEN** the client receives exactly one terminal event with the original response error and the stream completes normally
- **AND** the health-write failure is logged with exception information

#### Scenario: Keyed health persistence fails after ordered settlement

- **WHEN** a keyed continuation fails and its account-error health write raises after reservation settlement
- **THEN** settlement completes before the health write is attempted
- **AND** the client receives only the intended owner-unavailable terminal response

#### Scenario: Unanchored keyed terminal waits for committed settlement

- **WHEN** an unanchored request with an API-key reservation publishes a terminal upstream failure
- **THEN** its reservation settlement finishes before the account-error health write starts
- **AND** an ordinary health-write failure is logged while the single original terminal remains intact
