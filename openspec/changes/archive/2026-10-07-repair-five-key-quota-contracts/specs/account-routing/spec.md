## ADDED Requirements

### Requirement: Account quota restrictions survive process restarts

Per-account quota percentage restrictions SHALL persist in the account database and be read from fresh selection snapshots. Updating or clearing a restriction MUST invalidate account selection caches and propagate the routing change to replicas. Backup export and restore MUST preserve restrictions; legacy backups omitting the field MUST preserve an existing restriction. Existing documented standard-quota bypass paths MAY bypass the restriction.

#### Scenario: Another process reads the account limit

- **WHEN** an operator configures an account limit to 50 percent
- **THEN** a newly opened repository/session reads 50 percent
- **AND** normal selection excludes the account at 50 percent usage

#### Scenario: No usage is observed at zero percent

- **GIVEN** an account has a zero-percent restriction and no usage sample
- **WHEN** normal routing selects an account
- **THEN** the restricted account is excluded

#### Scenario: Account restriction is restored from backup

- **GIVEN** an exported account has a 50-percent restriction
- **WHEN** its restriction is cleared and the backup is restored
- **THEN** the account restriction is 50 percent again
- **AND** restoring an older backup that omits the field leaves it unchanged

## MODIFIED Requirements

### Requirement: Account quota limit restriction

The load balancing and selection system SHALL support per-account quota limit restrictions (`quota_limit_percent`). When a restriction is configured, the selector MUST compare the account's applicable quota percentages against the threshold and exclude it from ordinary selection when usage equals or exceeds that threshold. Restrictions MUST preserve the remaining headroom for external or cloud usage.

#### Scenario: Account below configured quota limit is eligible

- **GIVEN** an active account with a configured restriction of 50 percent
- **AND** its used quota is 40 percent
- **WHEN** ordinary account selection runs
- **THEN** the account remains eligible

#### Scenario: Account reaching configured quota limit is excluded

- **GIVEN** an active account with a configured restriction of 50 percent
- **AND** its used quota is 50 percent
- **WHEN** ordinary account selection runs
- **THEN** the account is excluded

#### Scenario: Account exceeding configured quota limit is excluded

- **GIVEN** an active account with a configured restriction of 50 percent
- **AND** its used quota is 55 percent
- **WHEN** ordinary account selection runs
- **THEN** the account is excluded

#### Scenario: Clearing a restriction restores eligibility

- **GIVEN** an active account is blocked only by its quota restriction
- **WHEN** the operator clears the restriction
- **THEN** ordinary selection includes the account again
