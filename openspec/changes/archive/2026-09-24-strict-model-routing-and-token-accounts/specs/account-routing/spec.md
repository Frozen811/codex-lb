# account-routing Specification Delta

## Requirements

### Requirement: Strict model-to-account routing

The proxy routing layer SHALL support strict model-to-account routing. When configured, requests for a mapped model MUST be routed exclusively to the designated account matching the target account ID, email, alias, or workspace identity.

The route mapping SHALL be configurable via local configuration and per-request routing headers (`x-codex-model-account-routing`). When a request matches a configured model route:
1. If the target account exists and is available, the request MUST be served by that account.
2. If the target account is missing, unavailable, rate-limited, cooling down, or outside the caller's scoped accounts, the proxy MUST fail the request with a routing error (`model_account_not_found`, `model_account_unavailable`, or `model_account_scope_mismatch`) instead of silently falling back to another account.
3. Unmapped models SHALL continue to use the standard load balancing strategy across eligible accounts.

#### Scenario: Request for mapped model routes strictly to designated account
- **GIVEN** a model route mapping `gpt-5.6-sol` to account `Account A`
- **AND** `Account A` is healthy and active
- **WHEN** a request arrives requesting model `gpt-5.6-sol`
- **THEN** `Account A` is selected to serve the request

#### Scenario: Request for mapped model fails closed when designated account is unavailable
- **GIVEN** a model route mapping `gpt-5.6-sol` to account `Account A`
- **AND** `Account A` is rate-limited or excluded
- **AND** other healthy accounts in the pool support `gpt-5.6-sol`
- **WHEN** a request arrives requesting model `gpt-5.6-sol`
- **THEN** the request fails closed with `model_account_unavailable`
- **AND** no alternate account is selected
