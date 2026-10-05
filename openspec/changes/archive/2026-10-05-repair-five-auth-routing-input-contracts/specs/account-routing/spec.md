## ADDED Requirements

### Requirement: Relative availability fallback retains persisted usage ordering

When eligible relative-availability candidates all have zero scores or zero draw weights, selection MUST compare persisted secondary usage, then persisted primary usage, before existing recency and account-ID tie breakers. A supplied selection seed MUST break only ties in persisted usage. Pressure-adjusted scoring MUST NOT erase the ordering of differently used accounts. Candidates without separately recorded persisted usage MUST retain their existing usage fallback behavior.

#### Scenario: Zero score fallback prefers the less used account

- **WHEN** two eligible accounts have persisted secondary usage of 95 and 38 percent but equal pressure-adjusted usage and zero availability scores
- **THEN** the 38-percent account is selected with and without a selection seed

#### Scenario: Zero draw weights retain persisted ordering

- **WHEN** eligible accounts have nonzero availability scores but all final draw weights are zero
- **THEN** selection prefers lower persisted secondary and primary usage
