# rate-limit-reset-credits Delta

## ADDED Requirements

### Requirement: Bulk redemption of eligible reset credits across accounts

The dashboard endpoint `POST /api/accounts/rate-limit-reset-credits/redeem-all` SHALL allow authorized operators to redeem all eligible banked reset credits across accounts in a single request. It SHALL accept an optional JSON payload with `account_ids: list[str]`. When `account_ids` is provided, redemption SHALL target only those specified accounts; when omitted or null, all eligible accounts in the repository SHALL be evaluated.

An account SHALL be eligible for bulk redemption only if:
- It is not marked for deletion (`delete_requested_at is None`),
- Its status is not in `_NON_REDEEMABLE_STATUSES` (`status != paused` and `status != deactivated`),
- It has a non-empty `chatgpt_account_id`,
- Its credentials are valid or usable (not failing `account_reauth_credentials_are_unavailable`),
- It has at least one banked reset credit (`available_count > 0` in its cached snapshot).

The endpoint SHALL redeem each account's own credits only, reusing the existing per-account redeem helper, durable ledger, and per-account serialization lock (`serialize_reset_credit_redeem`). It SHALL NOT pool credits across accounts. It SHALL report per-account success/failure in the response without failing the entire batch when an individual account encounters an error.

#### Scenario: Bulk redeem consumes all eligible credits across accounts
- **GIVEN** account A has 1 eligible reset credit
- **AND** account B has 2 eligible reset credits
- **AND** account C is paused with 1 credit
- **WHEN** the operator invokes `POST /api/accounts/rate-limit-reset-credits/redeem-all`
- **THEN** 1 credit is redeemed for account A
- **AND** 2 credits are redeemed for account B
- **AND** account C is skipped
- **AND** the response reports 3 total credits redeemed across 2 successful accounts

#### Scenario: Bulk redeem handles partial failures gracefully
- **GIVEN** account A has 1 eligible reset credit
- **AND** account B has 1 credit but its upstream consume call fails
- **WHEN** the operator invokes `POST /api/accounts/rate-limit-reset-credits/redeem-all`
- **THEN** account A succeeds and account B reports failure with an error message
- **AND** the overall response status is 200 with `total_accounts_succeeded: 1`
