## ADDED Requirements

### Requirement: Caller-scoped-out hard owners do not earn recovery waits

When a hard CODEX_SESSION owner is outside the caller's explicitly constrained allowed account pool, selection MUST report its existing hard-affinity failure as a caller exclusion and MUST NOT wait for that owner to recover inside the same fixed scope. The request MUST fail closed without upstream dispatch, sticky-owner retirement, or rebind. An owner that remains inside the allowed pool and is only temporarily unavailable MUST retain its existing bounded recovery behavior. An omitted pool constraint MUST remain unrestricted, and non-hard-affinity errors MUST retain their existing classification.

#### Scenario: Goal restart excludes its hard owner by API-key scope

- **WHEN** a goal restart's API key allows a replacement account but excludes the hard session owner
- **THEN** the request returns its existing hard-affinity failure without recovery polling or upstream dispatch
- **AND** the hard owner row and abandonment marker remain unchanged

#### Scenario: Scoped-in unhealthy owner can still recover

- **WHEN** the hard owner belongs to the allowed pool but is temporarily rate-limited or unavailable
- **THEN** it is not classified as caller-scoped-out
- **AND** the existing bounded recovery wait remains available
