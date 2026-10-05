## ADDED Requirements

### Requirement: Workspace exclusion preserves other records during refresh
Usage refresh MUST recognize the exact deactivated_workspace code as permanent evidence for only the selected routing record. Refresh of another workspace sharing an identity MUST NOT reactivate that record or deactivate the sibling.

#### Scenario: Identity has two workspaces
- **WHEN** refresh rejects one workspace as deactivated and refreshes its sibling successfully
- **THEN** the rejected workspace remains deactivated and the sibling remains eligible

