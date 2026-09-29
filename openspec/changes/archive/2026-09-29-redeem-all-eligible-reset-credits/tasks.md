# Tasks: Redeem all eligible reset credits in one action

- [x] Add `POST /api/accounts/rate-limit-reset-credits/redeem-all` endpoint in `app/modules/rate_limit_reset_credits/api.py` <!-- id: 0 -->
- [x] Add bulk redeem schemas `RedeemAllResetCreditsRequest`, `AccountRedeemResultItem`, and `RedeemAllResetCreditsResponse` <!-- id: 1 -->
- [x] Update frontend API client and types in `frontend/src/features/accounts/api.ts` and mutation hook in `use-accounts.ts` <!-- id: 2 -->
- [x] Add bulk redeem confirmation dialog and trigger in accounts surface <!-- id: 3 -->
- [x] Add integration and unit tests for bulk reset credit redemption <!-- id: 4 -->
- [x] Update main OpenSpec spec `openspec/specs/rate-limit-reset-credits/spec.md` <!-- id: 5 -->
