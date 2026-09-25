# account-import Specification Delta

## Requirements

### Requirement: Access-token-only credential imports and explicit metadata support

The account import service SHALL support importing credentials that contain only an `access_token` when `id_token` and `refresh_token` are omitted or empty.

When `id_token` is absent, the importer SHALL attempt to extract identity and claims from the `access_token` JWT payload if present. If neither token supplies specific identity fields, the importer SHALL accept explicit metadata in the import payload, including `email`, `plan_type`, `workspace_id`, `workspace_label`, `account_id`, and `seat_type`.

An account imported without a refresh token SHALL be marked as non-refreshable, with `refresh.state` reported as `non_refreshable` in auth status queries. The auth refresh manager SHALL NOT issue upstream token refresh requests for non-refreshable accounts.

#### Scenario: Importing an access-token-only credential with explicit metadata
- **GIVEN** an `auth_json` containing a valid `access_token` but omitting `id_token` and `refresh_token`
- **AND** explicit metadata specifying `email`, `plan_type`, and `workspace_id`
- **WHEN** the operator posts the file to `/api/accounts/import`
- **THEN** the account is successfully created in active status
- **AND** the account displays the provided email, plan, and workspace identity
- **AND** the account auth status reports refresh state as `non_refreshable`

#### Scenario: Refresh attempt on non-refreshable account fails without upstream dispatch
- **GIVEN** an account imported without a refresh token
- **WHEN** a token refresh is attempted on that account
- **THEN** a permanent refresh error is raised immediately without dispatching network calls upstream
