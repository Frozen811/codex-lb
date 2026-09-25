## Why

When an active account has not refreshed recently (e.g. `last_refresh` older than the refresh interval), `AuthManager.ensure_fresh` executes a preflight refresh before dispatching requests.
If that upstream refresh attempt encounters a credential-failure code (such as `refresh_token_invalidated`, `invalid_grant`, or `app_session_terminated`), the refresh token cannot be used.
However, if the account's existing `access_token` has not yet expired (e.g., `account_access_token_expires_at > time.time()`), discarding or blocking that valid access token immediately wastes the remaining unexpired session lifetime.
Instead, the account should be marked `REAUTH_REQUIRED` to prevent future background refresh loops and signal the operator, but the currently valid, unexpired access token must be retained so in-flight or immediate requests can continue until access expiry.

## What Changes

- In `AuthManager.ensure_fresh`:
  - When active preflight refresh fails with a permanent credential error (`refresh_token_invalidated`, `refresh_token_expired`, `invalid_grant`, `app_session_terminated`), re-read the fresh database row.
  - If the database row's access token is still unexpired (`account_access_token_expires_at(latest) > time.time()`), adopt the latest state (`_adopt_account_row(account, latest)`) and return without raising `RefreshError`.
  - The account status is set to `AccountStatus.REAUTH_REQUIRED` in the database, but requests can proceed using the unexpired access token.
- Add unit and integration tests covering the preflight retention behavior under various expiration states and upstream error codes.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `usage-refresh-policy`: Added requirement specifying that preflight refresh credential failure retains unexpired access tokens.

## Impact

- `app/modules/accounts/auth_manager.py`: Catches `RefreshError` with recognized credential failure codes in preflight, verifies `access_token` expiration, and adopts the existing credentials if still unexpired.
- Tests: `tests/integration/test_auth_preflight.py` and `tests/integration/test_proxy_responses.py`.
