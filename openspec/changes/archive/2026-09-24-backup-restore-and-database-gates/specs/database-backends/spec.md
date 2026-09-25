# database-backends Specification Delta

## Requirements

### Requirement: Verified SQLite-to-PostgreSQL migration path gate

Before deprecating or removing SQLite backend support, the project MUST provide and maintain a verified SQLite-to-PostgreSQL migration path.
A verification utility (`scripts/verify_sqlite_to_postgres_migration.py`) SHALL verify that:
1. Every table and column present in the SQLite schema maps cleanly to the PostgreSQL schema.
2. Data dump and translation preserve data types, foreign keys, timestamps, and JSON fields without loss or corruption.
3. The migration verification script exits with code 0 on a valid migration path and non-zero on schema or data inconsistencies.

#### Scenario: Verification script validates migration path
- **WHEN** `python scripts/verify_sqlite_to_postgres_migration.py` is executed
- **THEN** SQLite and PostgreSQL schema definitions and dump/load mechanisms are verified
- **AND** the check exits with code 0
