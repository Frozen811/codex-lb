## MODIFIED Requirements

### Requirement: Standalone Codex web search is forwarded faithfully

The proxy SHALL expose both `POST /backend-api/codex/alpha/search` and `POST /v1/alpha/search` through the same proxy-authenticated Codex control-request path used by other unary Codex control endpoints. The proxy MUST preserve the inbound request body and query parameters, MUST apply the existing API-key scope, account selection, token refresh, session affinity, failover, and upstream-route policies, and MUST forward the request to the upstream `POST /codex/alpha/search` path. Successful downstream responses MUST preserve the upstream status and body and MUST include only response headers allowed by the existing Codex control-response policy. Final non-2xx responses MUST preserve their status while using the existing Codex control OpenAI error-envelope normalization. The proxy MUST NOT parse, normalize, or invent a local schema for successful search requests or responses. Inbound `Content-Type` headers MUST NOT be duplicated in upstream headers.

#### Scenario: authenticated standalone search reaches the upstream Codex path via /v1

- **GIVEN** a valid proxy API key and at least one eligible ChatGPT account
- **WHEN** Codex sends `POST /v1/alpha/search` with a JSON body and query parameters
- **THEN** the proxy forwards the unchanged body and query parameters to `POST /codex/alpha/search` using the selected account credentials
- **AND** the downstream client receives the upstream status and body

#### Scenario: upstream headers do not contain duplicate content-type

- **GIVEN** an inbound control request with `content-type: application/json`
- **WHEN** the proxy constructs upstream request headers
- **THEN** the upstream headers contain exactly one case-insensitive `Content-Type` header
