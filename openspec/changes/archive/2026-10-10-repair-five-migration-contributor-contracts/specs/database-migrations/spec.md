## MODIFIED Requirements

### Requirement: Production-scale migration duration check gate

The migration safety gate MUST reject unbounded executable raw SQL updates on `request_logs`, `usage_history` and `additional_usage_history` in non-grandfathered revisions, irrespective of SQL keyword case or quoted/schema-qualified table identifiers. An unrelated `LIMIT` string MUST NOT establish bounded batching. The static check MUST remain runnable without application or database dependencies.

A separate duration benchmark MUST create isolated disposable test storage, upgrade to a baseline identified by an explicit revision or Git ref, seed a configurable synthetic request-log fixture with a default of at least three million rows, and execute migrations to the current head. It MUST report actual per-revision elapsed execution time, fixture size, backend and baseline. It MUST return non-zero on migration failure or an exceeded configurable duration budget, and MUST retain diagnostic timing artifacts on failure without disclosing database credentials. PostgreSQL benchmark execution MUST NOT reuse or clear an existing application database. CI MUST offer scheduled, migration-path and manual runs and expose per-revision timing summaries.

#### Scenario: Clean migrations pass duration check
- **WHEN** `python scripts/check_migration_durations.py` is executed
- **THEN** all migration files are analyzed
- **AND** the check exits with code 0

#### Scenario: Static unsafe update fails
- **WHEN** a non-grandfathered migration executes an unbounded update on a high-volume table
- **THEN** the static command exits non-zero and names the migration and table
- **AND** SQL case, qualification or an unrelated LIMIT literal does not suppress the violation

#### Scenario: Bounded or historical operation passes
- **WHEN** an update uses explicit bounded primary-key predicates or belongs to grandfathered history
- **THEN** the static gate accepts it without claiming measured runtime performance

#### Scenario: Real duration evidence
- **WHEN** the benchmark upgrades its seeded disposable database through pending revisions
- **THEN** the report identifies each executed revision and measured elapsed time
- **AND** a failed or over-budget revision makes the command fail while preserving its report
- **AND** setup and no-op execution are not invented migration timings

## ADDED Requirements

### Requirement: September SCIM and overflow histories converge immutably

The published September SCIM and overflow revision identifiers MUST remain unchanged and converge through their existing empty merge. A database at either parent or both parents MUST upgrade to the merged revision and onward to the canonical single head while retaining unrelated application rows. Downgrading only the merge MUST preserve both parent stamps and schemas; re-upgrading MUST restore a single merge stamp without rerunning parent operations. The topology collision exemption MUST apply only to the exact published pair after convergence and MUST reject additional revisions occupying its timestamp slot.

#### Scenario: Published parents and merge round trip
- **GIVEN** a populated database at either September parent or both parent stamps
- **WHEN** it upgrades to the merge, downgrades only that merge and re-upgrades
- **THEN** published identities, parent schemas and unrelated rows are preserved
- **AND** the subsequent upgrade reaches the canonical single head
