## ADDED Requirements

### Requirement: Native history and notes preserve opaque transport data

The proxy MUST preserve native history/notes POST body bytes, repeated query parameters and allowed `x-codex` encryption headers through canonical, `/v1/alpha/` and duplicated `/backend-api/codex/v1/alpha/` ingress, including trailing slash forms. All forms MUST use the same proxy authentication and account scope policies. GET notes operations MUST forward query parameters without synthesizing a request body.

#### Scenario: Encrypted notes payload reaches the selected account
- **WHEN** a scoped client sends a notes write with opaque body bytes, repeated query parameters and allowed encryption headers
- **THEN** the selected account receives the original bytes, query values and encryption headers on the canonical upstream operation
- **AND** only accounts in the API-key scope are eligible

#### Scenario: History and notes aliases enforce authentication
- **WHEN** API-key authentication is enabled and a client omits a valid key on a supported history or notes alias
- **THEN** the proxy rejects the request before upstream dispatch
