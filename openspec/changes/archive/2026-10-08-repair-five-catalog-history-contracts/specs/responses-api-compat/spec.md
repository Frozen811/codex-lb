## ADDED Requirements

### Requirement: Astra Cursor labels use canonical request fields

The proxy MUST normalize supported Cursor-style reasoning and speed suffixes on `gpt-6-astra` through the existing alias contract. An `extra-high-fast` label MUST forward the canonical model, high reasoning effort and priority service tier. Unknown suffixes MUST remain unchanged.

#### Scenario: Astra label reaches canonical upstream model
- **WHEN** a request uses `gpt-6-astra-extra-high-fast`
- **THEN** the upstream receives `gpt-6-astra` with high reasoning and priority service tier

### Requirement: Plugin catalog ingress forwards equivalent URL forms

Authenticated plugin catalog GET requests under `/ps/plugins/` and `/plugins/featured` MUST forward through pool credentials at the origin and equivalent `/backend-api` forms, including trailing slashes without redirects. The canonical upstream path MUST omit the ingress backend-api prefix and trailing slash. Repeated query parameters, upstream status/body and allowlisted response headers MUST be preserved. Unsupported methods MUST return HTTP 405 before upstream dispatch.

#### Scenario: Featured catalog trailing slash forwards directly
- **WHEN** a client reads `/backend-api/plugins/featured/` with repeated query parameters
- **THEN** one upstream GET receives `plugins/featured` and the original parameter sequence

#### Scenario: Plugin write is denied
- **WHEN** a client posts to a catalog ingress alias
- **THEN** it receives HTTP 405 without upstream dispatch
