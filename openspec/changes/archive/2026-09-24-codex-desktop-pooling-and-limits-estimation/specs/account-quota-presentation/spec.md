# account-quota-presentation Delta Specification

## Requirements

### Requirement: Codex Desktop usage preserves caller plan identity while pooling quota

When responding to Codex Desktop and Codex CLI usage endpoints (`/api/codex/usage`, `/backend-api/wham/usage`, and `/backend-api/codex/usage`), the proxy SHALL retain the signed-in caller's account `plan_type` while returning the aggregate quota windows, limits, and availability across the eligible account pool.

#### Scenario: Signed-in account retains plan identity with pooled capacity
- **GIVEN** a signed-in ChatGPT account with plan type `plus`
- **AND** another account in the pool with plan type `pro`
- **WHEN** Codex Desktop requests usage via `/api/codex/usage` or `/backend-api/wham/usage`
- **THEN** the returned payload `plan_type` reports `plus`
- **AND** the `rate_limit` details reflect aggregate pool utilization and availability
