## ADDED Requirements

### Requirement: Deactivated workspaces leave eligible failover selection
The exact upstream code deactivated_workspace MUST deactivate only the selected workspace routing record with a workspace-specific reason. An account-neutral request MUST be eligible to fail over before downstream-visible output. Hard-owned requests MUST NOT cross accounts or retry the unavailable owner. Keyed reservations MUST settle before terminal health writes. Unknown or code-less HTTP 402 responses MUST NOT be treated as permanent workspace evidence.

#### Scenario: Neutral request has a healthy alternative
- **WHEN** the selected workspace reports deactivated_workspace before output
- **THEN** a healthy eligible alternative can complete the request
- **AND** later selection excludes the deactivated record

#### Scenario: Owned or visible request
- **WHEN** a workspace rejection occurs on a hard-owned request or after output is visible
- **THEN** the original error is surfaced without replay on another account

#### Scenario: Payment-status rejection lacks workspace evidence
- **WHEN** upstream returns HTTP 402 with an unknown or absent code
- **THEN** the routing record remains active

