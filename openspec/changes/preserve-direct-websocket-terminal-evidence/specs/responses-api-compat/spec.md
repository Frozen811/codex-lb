## MODIFIED Requirements

### Requirement: Direct WebSocket terminal evidence preservation

When an upstream direct WebSocket connection ends abruptly with no upstream-authored close frame (`None` or adapter-synthesized RFC 6455 `1006`), the proxy MUST NOT write per-drop account error-health (`record_error`) on the serving account. When an already-selected continuity owner returns a retryable terminal event (such as `rate_limit_exceeded`, `usage_limit_reached`, or other retryable terminal event in `_WEBSOCKET_TRANSPARENT_REPLAY_ERROR_CODES`) and account migration is unsafe or refused, the proxy MUST surface the authentic upstream terminal event (including original error code, message, and retry hints) to the client, and MUST NOT rewrite the terminal event to `previous_response_owner_unavailable`.

#### Scenario: Direct WebSocket frame-less drop does not penalize account

- **GIVEN** an active direct WebSocket connection on account A
- **WHEN** the upstream WebSocket terminates abruptly with no close frame (`None` or 1006)
- **THEN** account A is not penalized with `record_error`

#### Scenario: Continuity owner terminal error is surfaced authentically

- **GIVEN** an anchored request connected to its continuity owner account A
- **WHEN** account A returns a retryable terminal event (e.g. `rate_limit_exceeded`)
- **AND** account migration is unsafe
- **THEN** the proxy records the error health on account A
- **AND** the proxy delivers the original terminal event (`rate_limit_exceeded`) to the downstream client without rewriting to `previous_response_owner_unavailable`
