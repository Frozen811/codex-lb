## ADDED Requirements

### Requirement: Credit windows are display-only overrides

Credit (`credits`) rules SHALL remain Codex usage-display overrides. Normal traffic MUST NOT accrue credits or be blocked by a credit rule. The editor MUST identify credit rules as display-only and explain that token and cost rules enforce traffic budgets. Existing credit counters and the legacy `/v1/usage` response MUST remain readable.

#### Scenario: A credit override is exhausted

- **GIVEN** a key has a credit override whose current value equals its maximum
- **WHEN** the key sends a request within its token and cost budgets
- **THEN** the credit override does not reject the request
- **AND** `/v1/usage` still reports the configured credit window

### Requirement: Dashboard observation windows apply to usage and trends

The API-key detail view SHALL offer 7, 30, 60, and 90-day observation windows with 7 days as the default. The selected window MUST apply to both its request/token/cost totals and its trend. Queries MUST distinguish observation windows in their cache keys and MUST NOT present the previous window's totals while the newly selected window is loading. Lifetime overview figures MUST retain their lifetime labels.

#### Scenario: Operator selects thirty days

- **WHEN** an operator selects the 30-day observation window
- **THEN** usage and trend requests both include `days=30`
- **AND** displayed detail labels identify the 30-day window

### Requirement: Bulk usage reset retains failed keys for retry

Bulk API-key usage reset MUST preserve credentials, key identities, rule configuration and request history. It MUST report failed key names and errors independently of successful resets, and retain failed keys as the retry selection.

#### Scenario: One selected key fails

- **GIVEN** an operator confirms resetting two keys
- **WHEN** one reset succeeds and the other fails
- **THEN** the successful key's counters are reset
- **AND** the failed key remains selected and its name and error are visible
