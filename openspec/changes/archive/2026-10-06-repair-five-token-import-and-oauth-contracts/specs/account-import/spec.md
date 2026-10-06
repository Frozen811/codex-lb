## ADDED Requirements

### Requirement: Credential import rejects blank access tokens

Single-file import and multi-account backup restore MUST reject empty or whitespace-only access tokens before account persistence or upstream I/O. Missing, empty, or whitespace-only optional ID and refresh tokens MUST represent absent credentials; they MUST NOT cause refresh dispatch or placeholder credential generation. Import validation errors MUST retain the dashboard envelope without echoing credential material.

#### Scenario: Blank access credential
- **WHEN** an operator uploads an auth file with an empty or whitespace-only access token
- **THEN** the API returns `invalid_auth_json` without creating an account
- **AND** no token material appears in the response

#### Scenario: Optional credential contains only whitespace
- **WHEN** an access-token-only import contains whitespace-only ID or refresh tokens
- **THEN** the account is imported using its access token and explicit metadata
- **AND** dashboard auth status reports `non_refreshable`

#### Scenario: Backup contains a blank access credential
- **WHEN** a backup restore includes an account with a whitespace-only access token
- **THEN** that entry is reported failed without creating an account
- **AND** other valid entries can still be restored

### Requirement: Non-refreshable preflight respects access-token validity

Normal preflight MUST permit a non-refreshable account with an unexpired or opaque access token. A forced refresh or a normal preflight with a known-expired access token MUST fail permanently before upstream token exchange or reusing that access token for a request. Existing proxy rejection handling MUST preserve credential-generation fencing and account-owned continuity.

#### Scenario: Opaque PAT remains usable
- **WHEN** normal preflight runs for a non-refreshable account whose access token has no locally known expiry
- **THEN** it returns the existing credentials without token exchange

#### Scenario: Forced repair cannot refresh a PAT
- **WHEN** an upstream access rejection triggers forced refresh of a non-refreshable account
- **THEN** preflight fails permanently without token exchange or returning the rejected token unchanged

#### Scenario: Known-expired access-only credential
- **WHEN** normal preflight sees a non-refreshable access token whose known expiry has passed
- **THEN** it fails with a permanent token-expiry error before upstream I/O

### Requirement: Dashboard supports explicit PAT entry

The dashboard account import dialog MUST offer both existing auth-file batches and access-token entry. Access-token entry MUST require a nonblank token, email and upstream account ID, offer Business/Enterprise plan selection and optional workspace metadata, and submit through the existing authorized import API. The token MUST be masked and MUST NOT be persisted in browser storage. Success or dismissal MUST clear the token. Pending import MUST block duplicate submission, mode changes and dismissal; failure MUST preserve editable input for retry.

#### Scenario: Operator pastes a PAT
- **WHEN** an operator selects access-token entry and supplies token, email and account ID
- **THEN** import uses the supplied plan/metadata and no refresh or ID token
- **AND** successful import clears the token and closes the dialog

#### Scenario: Pending import and retry
- **WHEN** access-token import is pending or fails
- **THEN** pending work cannot be duplicated or dismissed
- **AND** a failed import retains editable inputs for a deliberate retry

#### Scenario: File mode remains available
- **WHEN** an operator selects auth-file mode
- **THEN** sequential multi-file import and retry behavior remain available
