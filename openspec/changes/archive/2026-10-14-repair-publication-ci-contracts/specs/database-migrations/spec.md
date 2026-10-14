## ADDED Requirements

### Requirement: Sticky reallocation timing migration supports schema replay

The sticky reallocation timing migration MUST tolerate a settings schema created from current ORM metadata before its revision is recorded. It SHALL preserve existing timing values and unrelated settings or credentials, and SHALL add a non-null column with the `immediate` default when the column is absent.

#### Scenario: Existing settings receive the historical default

- **GIVEN** the settings table does not have sticky reallocation timing storage
- **WHEN** the migration upgrades the schema
- **THEN** existing settings rows have timing `immediate`
- **AND** unrelated settings remain unchanged

#### Scenario: Precreated timing storage retains its saved value

- **GIVEN** timing storage exists with a saved value of `after_compaction`
- **AND** its migration revision is still pending
- **WHEN** migration reconciliation upgrades to head
- **THEN** the upgrade succeeds without duplicate-column DDL
- **AND** the saved timing remains `after_compaction`

#### Scenario: Current metadata can replay an older migration ledger

- **GIVEN** the schema was created from current ORM metadata with an older or absent migration ledger
- **WHEN** startup or whole-chain migration replay reconciles the ledger
- **THEN** timing storage does not prevent completion
- **AND** existing settings and credentials are preserved
