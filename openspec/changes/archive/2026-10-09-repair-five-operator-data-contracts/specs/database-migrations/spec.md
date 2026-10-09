## ADDED Requirements

### Requirement: Online migration steps report private execution progress

Online migrations MUST report each revision's identity and direction before executing it and its elapsed time when execution succeeds or fails. Progress records MUST NOT contain SQL, parameters, database URLs, revision descriptions or exception text. Failed execution MUST preserve its original exception and stop later revisions. The migration framework MUST retain revision selection, transaction and version-table ownership; temporary progress instrumentation MUST be restored on every exit. Executed progress MUST NOT imply transaction commit. The migration CLI MUST enable progress on stderr and preserve stdout result formats. No-op runs MUST not invent executed revisions.

#### Scenario: Revision observes its own start record
- **WHEN** an online revision runs
- **THEN** its start record precedes its migration function and executed elapsed progress follows successful execution

#### Scenario: Failed revision preserves original failure privately
- **WHEN** a revision raises an error containing sensitive diagnostic text
- **THEN** progress names the failed revision and direction without that text
- **AND** the same exception propagates, later revisions do not execute and instrumentation is restored

#### Scenario: CLI and no-op output remains compatible
- **WHEN** the CLI upgrades to an already-current head
- **THEN** stdout retains current_revision and stderr does not invent an executed revision

### Requirement: Unknown revision failures explain conditional metadata recovery

An unknown database revision failure MUST preserve the refusal and explain that rollback-image metadata stamping requires verified schema and data compatibility, ended migration transactions, a recoverable database backup and encryption key, and a build containing both recorded and target revisions against the same database. Guidance MUST state that stamping changes only migration metadata and does not roll back schema or data. The failure MUST NOT stamp, mutate schema or bypass revision validation.

#### Scenario: Rollback image encounters an unknown revision
- **WHEN** an upgrade refuses a revision unknown to this build
- **THEN** the error includes conditional recovery prerequisites and metadata-only limitations
- **AND** the database is unchanged

#### Scenario: Unknown stamp still refuses
- **WHEN** an operator requests stamping to a revision absent from this build
- **THEN** the existing validation failure remains and no metadata is rewritten
