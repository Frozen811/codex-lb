# Safe refresh failure logging

The [refresh failure correlation requirement](specs/account-routing/spec.md#requirement-secret-safe-refresh-failure-correlation)
adds bounded diagnostic logging to `AuthManager` for failed refresh attempts.
Operators can track recurring refresh degradation without exposing private credentials,
account emails, raw identifiers, or arbitrary provider error content.

For example, when a refresh exchange fails with `refresh_token_revoked`, `AuthManager`
emits a warning with `account_ref=<16-char-sha256>`, `code=refresh_token_revoked`,
`permanent=True`, `transport=False`. Unknown or malformed provider error codes
are normalized to `"other"`, and exceptions are logged without traceback or raw
response payloads.
