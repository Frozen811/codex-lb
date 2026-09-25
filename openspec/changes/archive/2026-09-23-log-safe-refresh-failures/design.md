# Design

## Context

See [proposal.md](proposal.md). Token refresh failures in `AuthManager` previously lacked
structured diagnostics that correlate attempts without risking privacy violations.

## Goals / Non-Goals

Provide safe correlation of refresh attempts using a truncated SHA-256 account reference
and an allowlisted error category code. Do not log credentials, tokens, or untrusted provider strings.

## Decisions

- Pseudonymize the account identifier with `sha256(account_id.encode("utf-8")).hexdigest()[:16]`.
- Allowlist known safe error codes; map any unlisted or provider-tainted code to `"other"`.
- Keep flags `permanent` and `transport` boolean to prevent injection.
- Ensure `exc_info` is omitted from attempt failure warnings.
- Emit exactly one warning per failed attempt even when multiple callers join a singleflight refresh.
