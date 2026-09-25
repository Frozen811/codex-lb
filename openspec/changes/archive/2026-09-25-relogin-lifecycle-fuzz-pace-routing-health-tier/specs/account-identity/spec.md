# account-identity Specification Delta

## ADDED Requirements

### Requirement: Automated re-login lifecycle notifications

The system SHALL emit an authoritative audit event (`account_reauth_required`) whenever an account permanently fails authentication or token refresh and transitions into `REAUTH_REQUIRED` status. To preserve core simplicity principles (P1 and P2), browser automation and credential storage MUST NOT be embedded in core runtime. The emitted event MUST include `account_id`, `email`, and `deactivation_reason` to enable external automation and webhook listeners to initiate headless re-authentication and invoke account re-import or reactivation APIs.

#### Scenario: Account requires reauth and emits audit event
- **WHEN** token refresh fails permanently for an account
- **AND** the account transitions to `REAUTH_REQUIRED`
- **THEN** an audit event with action `account_reauth_required` is logged asynchronously
- **AND** the event details contain the account ID and deactivation reason

#### Scenario: External reauth runner updates account credentials
- **GIVEN** an account is in `REAUTH_REQUIRED` status
- **WHEN** an external re-authentication runner submits fresh credentials via `POST /api/accounts/import` or `POST /api/accounts/{id}/reactivate`
- **THEN** the account returns to active state without requiring in-core browser dependencies
