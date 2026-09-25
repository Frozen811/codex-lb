# Change: Strict Model Routing and Access Token Account Support

## Summary
Implements Batch 37 resolving Issues #1576, #1413, #1340, and #1130:
1. **Task 135 (Issue #1576)**: Strict model-to-ChatGPT OAuth account routing. Adds deterministic model-to-account routing mapping model slugs to designated ChatGPT accounts (by ID, email, alias, or workspace) with fail-closed behavior, available via `model_account_routing` configuration and per-request headers (`x-codex-model-account-routing`).
2. **Task 136 (Issue #1413) & Task 138 (Issue #1130)**: Explicit access-token-only credential imports and personal access token (PAT) accounts. Relaxes `AuthTokens` and `CodexAuthTokens` to make `id_token` and `refresh_token` optional strings, supports explicit metadata fields (`email`, `plan_type`, `workspace_id`, `workspace_label`, `account_id`, `seat_type`) in import payloads, parses JWT access token claims when `id_token` is omitted, and clearly marks and treats access-token-only accounts as non-refreshable without attempting failing upstream network refresh calls.
3. **Task 137 (Issue #1340)**: Simplicity backlog settings surface reduction verification. Verifies the reduction from 164 fields to 97 fields in `Settings` governed by `scripts/check_settings_tiers.py` and `.github/simplicity-budgets.toml`.

## Motivation
- Operators with multiple ChatGPT OAuth accounts need to direct specific models (e.g. `gpt-5.6-sol` vs `gpt-5.6-luna`) to specific accounts without needing fragmented client API keys.
- Users and enterprise automations using personal access tokens (PAT) or credential exports with only a valid `access_token` could not import their credentials because `id_token` and `refresh_token` were strictly required by the import schemas.
- Simplicity budgets and configuration tiers require strict enforcement to prevent settings bloat and ensure zero unintended surface expansion.

## Scope
- `app/core/auth/__init__.py`: Update `AuthTokens` and `AuthFile` to support optional `id_token` and `refresh_token`, access token JWT claims fallback, and explicit metadata fields.
- `app/modules/accounts/schemas.py`: Update `CodexAuthTokens`, `OpenCodeOAuthAuth`, and `AccountAuthExportTokens`.
- `app/modules/accounts/service.py`: Update `import_account` and `export_account` for access-token-only accounts.
- `app/modules/accounts/auth_manager.py`: Guard `_perform_refresh` to reject non-refreshable accounts gracefully without upstream network dispatch.
- `app/modules/accounts/mappers.py`: Return `refresh_state = "non_refreshable"` when `refresh_token` is missing or empty.
- `app/modules/proxy/model_account_routing.py`: Dedicated helper to resolve strict model-to-account mappings.
- `app/modules/proxy/service.py`: Hook model-to-account routing into `_select_account_with_budget`.
- OpenSpec specs: `account-routing` and `account-import`.
