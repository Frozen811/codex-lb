# Proposal: Redeem all eligible reset credits in one action

## Motivation

Operators managing pools with multiple accounts currently have to manually redeem banked reset credits one account at a time from the Accounts page, or wait for automatic redemption shortly before expiry (#1357 / #1358). Issue #2514 requests a one-click action on the Accounts surface to redeem all eligible banked reset credits across accounts.

## Scope & Invariants

- **Account Isolation**: Redeems each account's own credits only; no cross-account pooling (consistent with #2289).
- **Reuse Infrastructure**: Reuses the existing per-account redeem helper, durable ledger, and per-account serialization locks.
- **Operator Driven**: Default-off behavior requiring explicit operator action (never automatic).
- **Confirmation & Observability**: Provides a confirmation listing eligible accounts and credit counts to be consumed, with per-account success/error reporting and audit logging.
- **Safety**: Skips non-redeemable statuses (paused, deactivated, missing credentials, missing chatgpt_account_id).
