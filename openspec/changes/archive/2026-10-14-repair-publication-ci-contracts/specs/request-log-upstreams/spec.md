## ADDED Requirements

### Requirement: Upstream options preserve bounded legacy SQLite facets

Unfiltered request-log options that include upstream metadata MUST retain bounded legacy facet discovery. On SQLite, determining that a paired facet has no NULL value under its raw leading-value prefix SHALL use an indexed presence probe before applying live-row visibility predicates. A raw presence result MUST NOT expose soft-deleted or otherwise excluded rows.

#### Scenario: Missing NULL counterpart does not walk a legacy cohort

- **GIVEN** a legacy SQLite schema without the live-row facet indexes
- **AND** a leading status value has many rows and no NULL error-code counterpart
- **WHEN** unfiltered request-log options are requested
- **THEN** the missing NULL option is established without traversing that status cohort
- **AND** the existing option values and visibility filters are preserved
