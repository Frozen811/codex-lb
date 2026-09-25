# rate-limit-reset-credits Delta Specification

## Requirements

### Requirement: Codex Desktop reset credits are pooled across eligible imported accounts

When exposing rate-limit reset credits to Codex Desktop and Codex CLI through `/api/codex/usage`, `/backend-api/wham/usage`, and `/backend-api/codex/usage`, the proxy SHALL pool available reset credits across all eligible imported accounts in the rate-limit reset credits cache. When a reset credit redemption is requested via `/api/codex/rate-limit-reset-credits/consume` or its `/backend-api/*` aliases, the system SHALL locate the owning account of the target credit, execute the redemption against upstream with that owning account's credentials, and trigger a usage refresh for both the target account and the caller account.

#### Scenario: Codex Desktop displays pooled reset credits count
- **GIVEN** account A has 1 available reset credit
- **AND** account B has 2 available reset credits
- **WHEN** Codex Desktop requests usage
- **THEN** the returned `rate_limit_reset_credits.available_count` reports `3`

#### Scenario: Redeeming credit owned by another account in the pool
- **GIVEN** account A is the signed-in caller
- **AND** account B owns the requested redeem credit id
- **WHEN** Codex Desktop submits a consume request for that credit id
- **THEN** the redemption is executed against upstream using account B's credentials
- **AND** account B's cached reset credits snapshot is invalidated
- **AND** usage is refreshed for both account B and account A
