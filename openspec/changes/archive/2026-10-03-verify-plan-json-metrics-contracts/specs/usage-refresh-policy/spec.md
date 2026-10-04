## ADDED Requirements

### Requirement: Canonical Business Pro Lite plan compatibility

The service MUST canonicalize the upstream plan identifier `self_serve_business_prolite`, including case and surrounding whitespace variations, to the existing `prolite` tier during account import and usage refresh. Capacity and rate-limit plan metadata MUST use that canonical tier, and model eligibility MUST retain its Pro-equivalent entitlement. A workspace-less recognized account's paid-plan transition MUST accept the alias without changing its account identity or credentials. Unknown plan and conflicting-workspace payloads MUST retain existing admission guards.

#### Scenario: Workspace-less account refresh accepts paid alias
- **WHEN** a workspace-less team account receives usage for self_serve_business_prolite
- **THEN** canonical prolite metadata and usage are persisted and observable from a new session
- **AND** its identity and encrypted credentials are unchanged

#### Scenario: Imported alias has canonical capacity and entitlement
- **WHEN** an imported account reports the alias with mixed case and whitespace
- **THEN** its stored and dashboard plan is prolite with the same capacity and model eligibility as canonical prolite

#### Scenario: Alias does not override workspace identity
- **WHEN** an alias usage payload reports a conflicting workspace
- **THEN** the stored plan, workspace, and usage remain unchanged
