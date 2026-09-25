# query-caching Specification Delta

## Requirements

### Requirement: Projection history reads are bounded per account
The bulk history query used by projections (EWMA depletion, weekly-pace recent burn rate, weekly-pace smoothing mean) MUST support a per-account row cap that bounds the number of rows returned for each account to its newest rows inside the cutoff on both PostgreSQL and SQLite backends. Rows newer than the uncapped recent floor MUST be exempt from the cap on both backends so that equal-weight window averages (such as the smoothing window) are never truncated by a write burst.

#### Scenario: A write burst inside an equal-weight window is never truncated
- **GIVEN** an account that wrote more usage-history rows inside the smoothing or fleet-burn window than the per-account row cap
- **WHEN** the projections history fetch runs on PostgreSQL or SQLite
- **THEN** every in-cutoff row at or after the floor MUST be returned
- **AND** the weekly-pace smoothed values and fleet burn rate MUST equal the values the uncapped fetch would produce

#### Scenario: EWMA consumers agree with the full replay over the tail
- **GIVEN** an account with thousands of in-cutoff rows older than the floor
- **AND** the newest cap-many of those rows span at least cap-many distinct recorded seconds
- **WHEN** depletion or the weekly-pace recent burn rate is computed from the capped fetch and from the uncapped fetch
- **THEN** the EWMA rates MUST agree within the retained weight after cap-minus-one updates times the largest per-second sample slope in the history (an absolute bound on the rate)
- **AND** burn rate, risk, and exhaustion ETA MUST agree within that residual propagated through their formulas
- **AND** when a usage drop or window reset lands inside the returned tail the results MUST be identical

#### Scenario: Capped probes stay index-only
- **GIVEN** usage history rows for multiple accounts and a populated visibility map
- **WHEN** the capped per-account probe shape is EXPLAINed on PostgreSQL with sequential and bitmap scans disabled
- **THEN** the plan MUST serve each probe as an Index Only Scan over the covering indexes with no sequential scan of `usage_history`

#### Scenario: SQLite snapshot cache keeps the shared floor
- **GIVEN** an uncapped history fetch on the SQLite backend served through its snapshot cache
- **WHEN** per-account cutoffs are supplied without a per-account row cap
- **THEN** the SQLite snapshot-cache read MAY keep the shared floor and MAY ignore cutoffs
- **AND** per-account trimming in the caller MUST still bound each account's slice

#### Scenario: SQLite capped probes use composite index without temporary B-tree
- **GIVEN** usage history rows for multiple accounts in a SQLite database
- **WHEN** the capped per-account probe shape is EXPLAINed on SQLite
- **THEN** the plan MUST serve each probe using `idx_usage_window_account_latest` or `idx_usage_window_account_time_covering` (or raw-window twins) and MUST NOT use a temporary B-tree for sorting
