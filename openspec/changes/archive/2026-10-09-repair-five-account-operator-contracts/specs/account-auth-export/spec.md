## ADDED Requirements

### Requirement: Backup restore applies metadata to imported identity
Backup restore SHALL apply explicitly supplied alias, routing policy, warm-up enrollment and quota-limit metadata to the local account identity returned by credential import. Explicit null aliases and false warm-up enrollment SHALL clear those values. Export and restore SHALL preserve workspace identity metadata. A paused backup entry SHALL remain paused after restore; restore SHALL NOT reactivate an account paused by import routing policy.

#### Scenario: Source and destination identities differ
- **WHEN** a backup source ID differs from the local identity returned by import
- **THEN** metadata SHALL be applied only to the imported account
- **AND** explicit false and null values SHALL be restored.

#### Scenario: Paused portable account
- **WHEN** a paused account with workspace metadata is exported and restored
- **THEN** its workspace metadata SHALL round-trip and the restored account SHALL be paused.

#### Scenario: Older backup omits optional settings
- **WHEN** a backup entry omits alias, routing policy, warm-up enrollment or quota limit
- **THEN** restore SHALL preserve the corresponding existing setting.
