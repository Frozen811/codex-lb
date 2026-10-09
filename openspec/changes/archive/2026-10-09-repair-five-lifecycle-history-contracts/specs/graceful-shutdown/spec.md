## ADDED Requirements

### Requirement: Persistence observation preserves callback ownership
Internal drain status MUST report `request_persistence_state` as `pending`, `drained` or `unknown`. Registered persistence owners MUST remain pending until their ownership callbacks have finished, including completed tasks awaiting callback execution. A valid observation MUST include a nonnegative decimal `request_persistence_pending` count; an unavailable, throwing or invalid observation MUST report `unknown` without a count. Existing activity fields MUST remain available for valid observations. The observation MUST be nonblocking and MUST NOT claim historical write success.

#### Scenario: Completed settlement awaits ownership transfer
- **WHEN** a completed settlement task remains registered before its callback transfers fallback ownership
- **THEN** status reports pending with a positive count even if request and bridge counters are zero

#### Scenario: Observation is unavailable or malformed
- **WHEN** the persistence observer is missing, throws, or returns an invalid count or inconsistent activity fields
- **THEN** status reports unknown and omits the pending count

#### Scenario: Ownership has fully drained
- **WHEN** all registered persistence owners and their ownership callbacks have completed
- **THEN** status reports drained with count zero

### Requirement: Interrupted cancellation retains background ownership
A background database task that defers fallback cancellation MUST remain tracked if the task's stop caller is cancelled. Caller cancellation during cooperative grace MUST propagate without cancelling the worker. Pending cancelled work MUST prevent a clean-shutdown claim until it completes.

#### Scenario: Stop caller is cancelled during fallback cleanup
- **WHEN** a worker is unwinding database cleanup after fallback cancellation and its stop caller is cancelled
- **THEN** the worker remains tracked as undrained and caller cancellation propagates

#### Scenario: Stop caller is cancelled during cooperative grace
- **WHEN** the worker is finishing its unit of work and the grace-wait caller is cancelled
- **THEN** the worker remains running without forced cancellation

## MODIFIED Requirements

### Requirement: Graceful drain closes WebSocket admission

Once graceful drain begins, the application MUST reject every new external WebSocket connection before invoking the route handler. The rejection MUST be an HTTP denial response sent in place of the handshake (`websocket.http.response.start` followed by `websocket.http.response.body`), and MUST NOT be a pre-accept `websocket.close` frame, because ASGI servers surface a pre-accept close as an opaque HTTP `403` that clients treat as a terminal access error. The denial response MUST use HTTP status `503` and MUST carry a `Retry-After` header equal to the local overload retry-after value (`5`). For a proxy path (`/v1`, `/backend-api`, any path below them, or `/codex/responses` with or without its trailing slash) the body MUST be the OpenAI-style local-unavailable error envelope with `error.code = "proxy_unavailable"`, `error.type = "server_error"`, and `error.message = "Server is draining"`; for every other WebSocket path the body MUST be `{"detail": "Server is draining"}`. A Responses WebSocket scope admitted before the barrier MUST remain tracked until its handler exits. Other WebSocket protocols MUST receive the same late-admission rejection but MUST NOT hold the Responses in-flight counter for their full connection lifetime.

#### Scenario: New WebSocket arrives during drain

- **WHEN** a new WebSocket connection scope arrives after drain has begun
- **THEN** the application rejects the connection without invoking its route handler
- **AND** the rejected connection does not increase the in-flight count
- **AND** the rejection is an HTTP denial response with status `503` and `Retry-After: 5`, not a pre-accept `websocket.close` frame

#### Scenario: Proxy WebSocket upgrade is denied with the local-unavailable envelope

- **GIVEN** drain has begun
- **WHEN** a new WebSocket upgrade arrives at a proxy path such as `/v1/responses` or `/backend-api/codex/responses`
- **THEN** the client receives HTTP `503` with `Retry-After: 5`
- **AND** the JSON body carries `error.code = "proxy_unavailable"`, `error.type = "server_error"`, and `error.message = "Server is draining"`
- **AND** the server access log reflects `503` instead of `403 Forbidden`

#### Scenario: Non-proxy WebSocket upgrade is denied with a generic detail body

- **GIVEN** drain has begun
- **WHEN** a new WebSocket upgrade arrives at a non-proxy path such as `/ws/events`
- **THEN** the client receives HTTP `503` with `Retry-After: 5`
- **AND** the JSON body is `{"detail": "Server is draining"}`

#### Scenario: WebSocket crosses the drain barrier

- **WHEN** a Responses WebSocket scope is admitted immediately before drain begins
- **THEN** it remains in the in-flight count until its route handler exits
- **AND** shutdown waits for that scope within the configured drain timeout

#### Scenario: Realtime or Live connection predates drain

- **WHEN** a non-Responses WebSocket scope is admitted before drain
- **THEN** it does not hold the Responses in-flight counter
- **AND** normal Uvicorn connection shutdown remains its lifecycle bound

#### Scenario: Canonical Codex WebSocket denial retains the proxy envelope
- **WHEN** a WebSocket upgrade reaches `/codex/responses` or `/codex/responses/` during drain
- **THEN** denial uses HTTP 503, Retry-After 5 and the same OpenAI local-unavailable envelope as the equivalent proxy paths
- **AND** an unrelated non-proxy path remains a generic detail response

### Requirement: Internal drain status reports request-persistence activity

The `/internal/drain/status` endpoint MUST surface detached request-persistence activity alongside `in_flight` and bridge activity counters. If a valid persistence observation is available, the response payload `checks` dictionary MUST include `request_persistence_pending` (count of registered persistence owners awaiting ownership release), `request_persistence_active` (boolean indicating whether any persistence owners remain registered), `api_key_settlements_pending` (count of registered API-key reservation and settlement owners), and `persistence_drain_active` (boolean indicating whether persistence work is currently blocking completion of drain).

#### Scenario: Internal drain status reflects pending persistence tasks

- **GIVEN** a server undergoing graceful drain with zero in-flight responses
- **WHEN** detached background persistence or API-key settlement tasks are still executing
- **THEN** `/internal/drain/status` reports `request_persistence_pending` as the number of registered owners
- **AND** reports `request_persistence_active = "true"` and `persistence_drain_active = "true"`

#### Scenario: Internal drain status reflects settled persistence tasks

- **GIVEN** a server undergoing graceful drain with zero in-flight responses
- **WHEN** all background persistence and settlement owners and their callbacks have completed
- **THEN** `/internal/drain/status` reports `request_persistence_pending = "0"`
- **AND** reports `request_persistence_active = "false"` and `persistence_drain_active = "false"`
