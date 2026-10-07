## MODIFIED Requirements

### Requirement: Frontend flow checks avoid cold-route and fixture overhead

Frontend integration checks SHALL preload visited lazy routes outside the timed
interaction body when needed to preserve the existing timeout. They SHALL keep
the real App, route guards, interaction semantics and behavior assertions.
Firewall flow cases MUST start with fresh auth initialization and mutable mock
storage, and independently verify Advanced expansion, IP creation, confirmed
IP removal and legacy routing within the unchanged timeout. Target discovery
optimizations MUST preserve checks of the actual controls' roles and visibility.
Cache-probe API fixtures MUST cover plan and confirmed run requests with typed,
deterministic responses; unknown API requests MUST remain errors.

#### Scenario: Firewall add/remove runs with coverage

- **WHEN** Settings integration checks add and remove an IP with coverage
- **THEN** they verify the stored IP and its removal through real UI interactions
- **AND** each case owns fresh auth and mock storage without raising timeouts or retrying failed tests

#### Scenario: Advanced settings fetches the cache-probe plan

- **WHEN** the real Settings route opens its Advanced group in an MSW test
- **THEN** the cache-probe plan request has a registered schema-valid handler
- **AND** a confirmed run has a deterministic schema-valid result
