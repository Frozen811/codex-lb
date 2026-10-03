## ADDED Requirements

### Requirement: Remote reverse-proxy instructions preserve application transport

Remote deployment guidance MUST provide a concrete reverse-proxy example that preserves Host including port, forwards WebSocket upgrades, disables response buffering for SSE, and bounds upstream timeouts. It MUST retain dashboard bootstrap and client API-key requirements and identify TLS termination and OAuth callback setup separately from basic proxy startup.

#### Scenario: Proxy a dashboard request and a streaming client

- **WHEN** an operator follows the documented reverse-proxy example
- **THEN** readiness and dashboard assets are reachable through the proxy
- **AND** request identity is preserved for dashboard origin checks
- **AND** HTTP streaming and WebSocket upgrade traffic reach the application
