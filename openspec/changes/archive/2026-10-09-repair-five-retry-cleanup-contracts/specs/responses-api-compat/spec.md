## MODIFIED Requirements

### Requirement: Retry Circuit Scheduled Purge Fencing
The durable bridge repository scheduled purge for stale retry circuits (`purge_retry_circuits_before`) SHALL fence each deletion against the selected observation timestamp, admission generation, consecutive failure count and null-safe last failure detail. A candidate changed between selection and deletion SHALL NOT be selected again in the same cleanup pass. Unchanged old rows SHALL remain eligible under the existing age and continuity rules.

#### Scenario: Stale retry circuit candidate updated before deletion
- **GIVEN** a stale candidate observed at timestamp T0, generation G0 and failure count F0
- **WHEN** a concurrent operation changes any of those values before deletion
- **THEN** that cleanup deletion matches zero rows
- **AND** the candidate survives the entire cleanup pass, including when other candidates are deleted successfully

#### Scenario: Lagging-clock failure preserves the timestamp
- **GIVEN** a stale candidate observed at timestamp T0 and failure count F0
- **WHEN** a newer failure increments the count without advancing T0
- **THEN** scheduled cleanup preserves that row

#### Scenario: Failure detail changes without advancing other fences
- **GIVEN** a stale candidate whose timestamp, admission generation and failure count remain unchanged
- **WHEN** its last failure detail changes before deletion, including a transition to or from NULL
- **THEN** scheduled cleanup preserves that candidate for the rest of the pass
- **AND** unrelated unchanged candidates remain eligible for deletion

#### Scenario: Unchanged nullable failure detail
- **WHEN** an otherwise eligible stale candidate retains its selected last failure detail, including NULL
- **THEN** scheduled cleanup deletes that candidate under the existing age and continuity rules
