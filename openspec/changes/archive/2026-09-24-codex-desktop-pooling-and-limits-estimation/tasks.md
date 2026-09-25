# Tasks: Codex Desktop Pooling and Limits Estimation

- [ ] 1. Codex Desktop Quota and Reset Credits Pooling <!-- id: codex-desktop-pooling -->
  - [ ] 1.1 Add route aliases for `/backend-api/wham/usage`, `/backend-api/codex/usage`, `/backend-api/wham/rate-limit-reset-credits/consume`, and `/backend-api/codex/rate-limit-reset-credits/consume` in `app/modules/proxy/api.py`.
  - [ ] 1.2 In `_attach_codex_usage_reset_credits`, pool available credits across all accounts in `RateLimitResetCreditsStore` instead of strictly caller's account.
  - [ ] 1.3 In `codex_usage`, preserve caller's `plan_type` from `codex_usage_identity_payload` when available.
  - [ ] 1.4 In `codex_consume_rate_limit_reset_credit`, support redeeming credits owned by other accounts in the pool, refreshing both the target account and the caller account.
  - [ ] 1.5 Add integration tests covering pooled credits and quota endpoints.

- [ ] 2. Weekly Limits Estimation in $ <!-- id: weekly-limits-estimation -->
  - [ ] 2.1 Add `estimated_full_weekly_limit_cost_usd` and `used_cost_usd` fields to `WeeklyCreditPaceResponse` in `app/modules/dashboard/schemas.py`.
  - [ ] 2.2 Update `build_weekly_credit_pace` in `app/modules/dashboard/weekly_pace.py` and `app/modules/dashboard/service.py` to calculate full 100% weekly limit estimated cost.
  - [ ] 2.3 Update frontend schemas in `frontend/src/features/dashboard/schemas.ts` and card in `frontend/src/features/dashboard/components/weekly-credits-pace-card.tsx`.
  - [ ] 2.4 Add localization keys to `en.json`, `ko.json`, and `zh-CN.json`.

- [ ] 3. Model Sources Compatibility for ChatGPT OAuth <!-- id: model-sources-oauth -->
  - [ ] 3.1 In `app/modules/model_sources/catalog.py`, parse `available_in_plans` from `raw` or default to `frozenset({"free", "plus", "pro", "team", "edu"})`.
  - [ ] 3.2 Verify `GET /models` and `GET /backend-api/codex/models` output includes `available_in_plans`.
  - [ ] 3.3 Add unit test verifying model source models expose `available_in_plans`.
