# api-keys Specification Delta

## ADDED Requirements

### Requirement: Configurable observation windows for API key usage

The system SHALL allow querying API key usage across configurable observation windows via `GET /api/api-keys/{key_id}/usage`. The endpoint MUST accept a `days` query parameter bounded between 1 and 90 (inclusive, default 7). The response MUST return `key_id`, `days`, `total_tokens`, `total_cost_usd`, `total_requests`, `cached_input_tokens`, and `account_costs[]`. The `GET /api/api-keys/{key_id}/trends` endpoint SHALL also accept an optional `days` query parameter (1-90, default 7). The legacy `GET /api/api-keys/{key_id}/usage-7d` endpoint MUST remain functional as a backward-compatible alias.

#### Scenario: Query API key usage with custom observation window
- **WHEN** a client requests `GET /api/api-keys/{key_id}/usage?days=30`
- **THEN** the system returns aggregated usage totals and account costs for the past 30 days
- **AND** the response contains `days = 30`

#### Scenario: Query API key usage with invalid observation window is rejected
- **WHEN** a client requests `GET /api/api-keys/{key_id}/usage?days=0` or `GET /api/api-keys/{key_id}/usage?days=91`
- **THEN** the system returns HTTP 422 Unprocessable Entity
