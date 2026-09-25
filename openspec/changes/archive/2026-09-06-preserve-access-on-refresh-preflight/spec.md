# Delta Spec: Retain Unexpired Access on Refresh Preflight Failure

## Capability: `usage-refresh-policy`

### Requirement: Preflight refresh credential failure retains unexpired access tokens

When an account undergoes active preflight refresh in `ensure_fresh` and the upstream refresh exchange fails with a recognized permanent credential failure code (`refresh_token_invalidated`, `refresh_token_expired`, `invalid_grant`, `app_session_terminated`), the system MUST re-read the latest account row from the database.
If the freshly re-read account's access token expiration is strictly in the future (`account_access_token_expires_at > time.time()`), the system MUST adopt the row without raising a `RefreshError`, allowing callers to continue using the unexpired access token.

#### Scenario: Unexpired access token is retained after preflight refresh revocation
- **GIVEN** an active account with an unexpired access token whose `last_refresh` warrants preflight refresh
- **WHEN** preflight refresh receives `refresh_token_invalidated` from upstream
- **THEN** the account is marked `reauth_required` in the database
- **AND** `ensure_fresh` does not raise `RefreshError`
- **AND** the unexpired access token is returned and dispatched upstream
