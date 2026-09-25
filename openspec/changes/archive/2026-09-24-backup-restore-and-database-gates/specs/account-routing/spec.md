# account-routing Specification Delta

## Requirements

### Requirement: Account quota limit restriction

The load balancing and selection system SHALL support per-account quota limit restrictions (`max_quota_percent`).
When a quota limit restriction is configured for an account (e.g., 50.0%), the selector SHALL compare the account's current used quota percentage against the restriction threshold.

If an account's used quota percentage exceeds the configured limit restriction, the account SHALL be treated as exhausted and excluded from ordinary load balancing selection, preserving the remaining headroom for external or cloud usage.

#### Scenario: Account below configured quota limit is eligible
- **GIVEN** an active account with a configured limit restriction of 50.0%
- **AND** the account's recorded used quota is 40.0%
- **WHEN** account selection runs
- **THEN** the account remains eligible for selection

#### Scenario: Account exceeding configured quota limit is excluded
- **GIVEN** an active account with a configured limit restriction of 50.0%
- **AND** the account's recorded used quota is 55.0%
- **WHEN** account selection runs
- **THEN** the account is treated as exhausted and excluded from candidate selection
