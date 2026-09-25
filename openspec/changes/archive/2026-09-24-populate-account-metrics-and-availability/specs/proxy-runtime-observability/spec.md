# proxy-runtime-observability Specification Delta

## ADDED Requirements

### Requirement: Account count and availability metrics

The Prometheus metrics endpoint MUST export `codex_lb_accounts_total` by status and `codex_lb_accounts_available` reflecting the current pool state.

#### Scenario: All account statuses are reported with exact counts

- **GIVEN** a pool with 2 active accounts and 1 rate-limited account
- **WHEN** account metrics are recorded
- **THEN** `codex_lb_accounts_total{status="active"}` equals 2
- **AND** `codex_lb_accounts_total{status="rate_limited"}` equals 1
- **AND** `codex_lb_accounts_total` for every other status in `AccountStatus` equals 0

#### Scenario: Available account gauge reflects routable accounts

- **GIVEN** a pool with 2 active accounts, where 1 active account is marked routing-unavailable
- **WHEN** account metrics are recorded
- **THEN** `codex_lb_accounts_available` equals 1
- **AND** clearing the unavailable mark on that account updates `codex_lb_accounts_available` to 2
