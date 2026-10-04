## ADDED Requirements

### Requirement: Capped projection history reads

Projection history reads with a per-account row cap MUST accept only nonnegative integers, excluding booleans, and MUST reject invalid caps before database queries. Capped reads MUST return the newest eligible rows per requested account in ascending timestamp and ID order, respect the global floor and tighter account cutoffs, and preserve all eligible rows at or after an explicit recent floor. SQLite capped reads MUST avoid hydrating the entire older history or populating the uncapped history cache.

#### Scenario: Dense SQLite history
- **WHEN** projection history is requested with cap 64 for a densely sampled account
- **THEN** no more than 64 rows older than the explicit recent floor are returned for that account
- **AND** all eligible recent-floor samples are retained with deterministic tie ordering

#### Scenario: Invalid or zero cap
- **WHEN** a cap is negative, boolean or non-integer
- **THEN** the read fails with a validation error before executing a database query
- **WHEN** the cap is zero
- **THEN** only eligible recent-floor samples can be returned
