## ADDED Requirements

### Requirement: Quota restriction storage survives ledger recovery

Locked startup and CLI upgrades MUST preserve an existing nullable floating-point `accounts.quota_limit_percent` column and its values when the Alembic ledger does not record its published additive revision. Recovery MUST apply pending ancestor migrations before marking that quota-only revision applied, MUST preserve the caller's resolved target including relative targets, and MUST reject incompatible quota columns without applying or recording the quota-only revision. Missing columns MUST use the ordinary migration path, and published revisions MUST remain unchanged.

#### Scenario: Compatible quota column exists with an older or missing ledger
- **WHEN** an upgrade crosses the quota restriction revision over compatible existing storage
- **THEN** pending ancestors are applied and the quota-only revision is recorded without duplicate column DDL
- **AND** account credentials and quota restriction values are preserved

#### Scenario: Relative target crosses the quota revision
- **WHEN** a relative upgrade target resolves to the quota restriction revision
- **THEN** recovery ends at that same resolved target

#### Scenario: Quota column is absent
- **WHEN** an upgrade crosses the quota restriction revision and its column is absent
- **THEN** the published migration creates nullable floating-point storage normally

#### Scenario: Existing quota storage is incompatible
- **WHEN** the existing quota column is not nullable floating-point storage without a server default
- **THEN** upgrade fails with an explicit schema error without applying or recording the quota-only revision
