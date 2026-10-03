## ADDED Requirements

### Requirement: Update and rollback guidance selects source and paired storage explicitly

Update instructions MUST identify the intended fork repository independently of local remote names. They MUST distinguish a cached mutable image tag, a pinned digest, source revision, package metadata and runtime version. They MUST instruct operators to preserve DB/key/configuration, stop old writers before replacement, prepare changed frontend assets, and verify selected executable/image and retained application data after recreation. Rollback MUST use a compatible old executable and its paired pre-upgrade database/key snapshot unless an explicitly verified migration-specific downgrade applies.

#### Scenario: Origin points at upstream

- **WHEN** an operator follows fork source update instructions in a checkout whose origin points at upstream
- **THEN** the instructions explicitly fetch/select the intended fork source
- **AND** do not merge or update from origin merely because of its remote name

#### Scenario: Recreate and restore an isolated installation

- **WHEN** an operator follows the verified update/rollback rehearsal
- **THEN** runtime/image identity and preserved settings/account decryptability are checked separately
- **AND** rollback does not assume an older image can open a newer schema
