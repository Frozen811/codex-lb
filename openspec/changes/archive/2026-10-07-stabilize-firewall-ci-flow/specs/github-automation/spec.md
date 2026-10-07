## ADDED Requirements

### Requirement: Frontend flow checks avoid cold-route and fixture overhead

Frontend integration checks SHALL preload visited lazy routes outside the timed
interaction body when needed to preserve the existing timeout. They SHALL keep
the real App, route guards, interaction semantics and behavior assertions.
Cache-probe API fixtures MUST cover plan and confirmed run requests with typed,
deterministic responses; unknown API requests MUST remain errors.

#### Scenario: Firewall add/remove runs with coverage

- **WHEN** a Settings integration check adds and removes an IP with coverage
- **THEN** it verifies the stored IP and its removal through real UI interactions
- **AND** it does not raise test timeouts or retry a failed test

#### Scenario: Advanced settings fetches the cache-probe plan

- **WHEN** the real Settings route opens its Advanced group in an MSW test
- **THEN** the cache-probe plan request has a registered schema-valid handler
- **AND** a confirmed run has a deterministic schema-valid result
