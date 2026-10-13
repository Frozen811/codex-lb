## ADDED Requirements

### Requirement: Bulk remaining credits use authoritative ownership
After a successful bulk consume with remaining credits, the system SHALL obtain actual remaining credit identities through the owning account's existing upstream route before another consume. It SHALL NOT fabricate credit IDs or replace a newer cache generation with an older observation. A failure after partial success SHALL retain the completed consume count and per-account error while allowing later accounts to proceed.

#### Scenario: Consumed credit was not first in the cached list
- **WHEN** the authoritative account response chooses a credit other than the first cached entry
- **THEN** subsequent bulk redemption SHALL use the authoritative remaining IDs.

#### Scenario: Partial failure and independent account
- **WHEN** one account succeeds once and fails on a later consume
- **THEN** the batch SHALL retain that success and error and SHALL process another eligible account.

#### Scenario: Cache invalidation races observation
- **WHEN** a new cache generation is installed while remaining credits are fetched
- **THEN** the older observation SHALL NOT overwrite it.

### Requirement: Paused reset-credit cached visibility does not grant redemption
The dashboard SHALL retain cached reset-credit count and expiry for paused accounts while excluding them from background polling and bulk/manual redemption. A selected-account observation SHALL preserve paused status and SHALL NOT consume a credit.

#### Scenario: Paused account with cached credits
- **WHEN** a paused account has cached credits and an operator lists accounts or observes its reset-credit count
- **THEN** cached visibility and observation SHALL remain available
- **AND** polling and redemption SHALL remain blocked.
