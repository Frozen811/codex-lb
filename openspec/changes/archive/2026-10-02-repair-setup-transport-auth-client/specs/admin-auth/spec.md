## MODIFIED Requirements

### Requirement: Trusted-header identity evidence is singular

The system MUST create a trusted-header dashboard principal only when a trusted captured raw proxy peer supplies exactly one occurrence of the configured identity field and its trimmed value is non-empty. Both identity-header sanitization and principal resolution MUST authorize the raw socket peer independently of a forwarded client address. Missing captured socket provenance MUST fail closed. The system MUST treat two or more occurrences as ambiguous regardless of field-name casing, field order, value equality, or whether another occurrence is empty. Ambiguous identity evidence MUST NOT produce an authenticated principal or actor.

#### Scenario: Duplicate trusted identity fields are rejected

- **WHEN** a trusted raw proxy peer sends two or more occurrences of the configured dashboard identity field
- **THEN** a protected dashboard request returns HTTP 401 with error code `proxy_auth_required`
- **AND** no trusted-header principal or actor is produced

#### Scenario: One non-empty trusted identity field authenticates

- **WHEN** a trusted raw proxy peer sends exactly one configured dashboard identity field with a non-empty trimmed value
- **THEN** the system authenticates an admin principal with that trimmed value as the actor

#### Scenario: Forwarded remote client differs from trusted proxy

- **WHEN** a trusted socket proxy projects a remote user's IP outside the trusted proxy CIDRs
- **AND** supplies one valid configured identity field
- **THEN** the identity authenticates and retains the asserted actor
- **AND** the projected user IP remains available for locality and firewall decisions

#### Scenario: Forwarded trusted-looking client cannot authorize an untrusted socket

- **WHEN** an untrusted or uncaptured socket sends a trusted-looking forwarded IP and an identity field
- **THEN** it does not receive a trusted-header principal
