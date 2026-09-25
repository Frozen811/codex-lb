# frontend-architecture Specification Delta

## ADDED Requirements

### Requirement: Recent requests model source visibility

When a request log entry has no associated account (`accountId` is null) but was routed to an upstream model source (`modelSourceId` is present), the dashboard recent-requests table MUST render the model source identifier in the account column instead of `Unassigned`. The request details dialog MUST display the `modelSourceId` and `modelSourceKind` under request metadata.

#### Scenario: Model source request renders model source identifier in account column
- **GIVEN** a request log entry where `accountId` is null and `modelSourceId` is populated
- **WHEN** the recent-requests table renders the row
- **THEN** the account column displays the `modelSourceId`
- **AND** the column does not display `Unassigned`

#### Scenario: Request details dialog displays model source metadata
- **GIVEN** a selected request log entry with a populated `modelSourceId`
- **WHEN** the user opens the request details dialog
- **THEN** the dialog displays the model source identifier under `Model Source`
- **AND** displays `modelSourceKind` under `Source Kind` when present
