# request-log-upstreams Specification

## Purpose

Provide locally observable request log upstreams with explicit identity, scope and compatibility limits.

## Requirements

### Requirement: Observed upstream filtering preserves identity and exact counts
Request-log list and options APIs SHALL accept repeated `upstream` values with OR semantics, combined with existing filters using AND semantics. `subscription_pool` SHALL select NULL model-source IDs including failures before account selection. Other values SHALL match stable model-source IDs. Active upstream selections MUST use exact raw counts and independent count-cache identities. Options SHALL ignore their own upstream selection while other facets honor it, exclude soft-deleted logs, and enumerate unfiltered IDs using indexed skip scans plus an indexed NULL presence probe. Options SHALL resolve current names and persisted kinds without exposing credentials or URLs; deleted sources SHALL retain stable-ID options. Existing requests without this parameter SHALL retain their behavior.

#### Scenario: Mixed and deleted upstream traffic
- **WHEN** logs contain subscription failures, two sources with the same model, and a deleted source
- **THEN** mixed selections return the exact union and total
- **AND** source options retain stable IDs and deleted status without secrets

#### Scenario: Facet self-exemption
- **WHEN** one upstream is selected
- **THEN** upstream options still offer other matching upstreams
- **AND** other facets reflect the upstream selection

### Requirement: Upstream options preserve bounded legacy SQLite facets

Unfiltered request-log options that include upstream metadata MUST retain bounded legacy facet discovery. On SQLite, determining that a paired facet has no NULL value under its raw leading-value prefix SHALL use an indexed presence probe before applying live-row visibility predicates. A raw presence result MUST NOT expose soft-deleted or otherwise excluded rows.

#### Scenario: Missing NULL counterpart does not walk a legacy cohort

- **GIVEN** a legacy SQLite schema without the live-row facet indexes
- **AND** a leading status value has many rows and no NULL error-code counterpart
- **WHEN** unfiltered request-log options are requested
- **THEN** the missing NULL option is established without traversing that status cohort
- **AND** the existing option values and visibility filters are preserved
