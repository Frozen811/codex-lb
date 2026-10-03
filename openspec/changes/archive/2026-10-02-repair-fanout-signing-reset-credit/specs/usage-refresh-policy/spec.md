## ADDED Requirements

### Requirement: Cross-account reset credit consumption requires target identity

When a ChatGPT caller consumes a pooled credit belonging to another account, the Codex-compatible consume endpoint and its slash and backend aliases MUST require a nonempty ChatGPT account ID on the refreshed target credentials. A missing target ID MUST return HTTP 401 with the OpenAI authentication error envelope before credit consumption dispatch, invalidate no credit snapshots, and perform no post-redemption usage refresh. A valid target MUST be consumed with that target's credentials and its original redemption ID.

#### Scenario: Missing target ChatGPT account ID
- **WHEN** an authenticated caller requests a pooled credit whose refreshed target lacks a ChatGPT account ID
- **THEN** consumption is refused with HTTP 401, `invalid_api_key`, and `authentication_error`, without dispatch or credit mutation

#### Scenario: Target identity is present
- **WHEN** an authenticated caller requests a pooled credit with a valid refreshed target identity
- **THEN** consumption uses the target bearer token, target ChatGPT account ID, and original redemption ID
