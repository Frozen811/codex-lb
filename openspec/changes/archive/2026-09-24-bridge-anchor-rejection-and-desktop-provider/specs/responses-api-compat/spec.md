# responses-api-compat Specification Delta

## ADDED Requirements

### Requirement: Native transport failure lifecycle

Native Codex streaming clients expect a terminal SSE event or structured transport failure handling when an upstream stream fails. When an HTTP bridge native stream encounters a synthetic transport failure or an upstream rejection of a proxy-injected anchor (`bridge_previous_response_not_found`), the proxy MUST deliver a terminal SSE `response.failed` event if the HTTP 200 headers have already been committed (including after keepalive events have been sent), and MUST NOT abruptly terminate the socket without a terminal event.

#### Scenario: Native client receives terminal event after keepalive on rejected anchor

- **GIVEN** a native Codex streaming request to the HTTP bridge
- **AND** a keepalive event has been written to the client
- **WHEN** upstream rejects the anchor with `previous_response_not_found`
- **THEN** the bridge yields an SSE `response.failed` terminal event
- **AND** the HTTP connection does not abort with an unexpected EOF or disconnect before completion

#### Scenario: Startup probe classifies bridge_previous_response_not_found as native transport failure

- **GIVEN** a native Codex streaming request encountering `bridge_previous_response_not_found` during startup probe
- **WHEN** the startup error is evaluated
- **THEN** it is classified as a native transport failure
- **AND** the client receives a stream carrying a terminal retryable event instead of a raw JSON 502 error
