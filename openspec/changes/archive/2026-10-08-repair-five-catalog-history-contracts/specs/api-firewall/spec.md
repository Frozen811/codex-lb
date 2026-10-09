## ADDED Requirements

### Requirement: Plugin catalog aliases share firewall enforcement

Plugin catalog ingress at origin and backend-api aliases, including trailing slashes, MUST enforce the same IP allowlist before account selection or upstream dispatch.

#### Scenario: Unlisted address cannot access a catalog alias
- **WHEN** the firewall allowlist excludes a client's address and the client reads a supported plugin catalog alias
- **THEN** the request returns HTTP 403 ip_forbidden without upstream dispatch
