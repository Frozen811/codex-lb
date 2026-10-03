## ADDED Requirements

### Requirement: Standalone search ingress aliases are slash equivalent

The proxy MUST serve `POST /backend-api/codex/alpha/search`, `POST /v1/alpha/search` and their duplicated Codex-prefix alias, both with and without a trailing slash, directly without redirecting. Every form MUST retain the existing authenticated control request, account scope, response normalization and media-type policy.

#### Scenario: Search trailing slash dispatches directly
- **WHEN** a client posts an opaque search body to any supported ingress form ending in `/`
- **THEN** the request reaches the upstream `codex/alpha/search` operation without an HTTP redirect
- **AND** original body bytes and repeated query parameters are preserved
