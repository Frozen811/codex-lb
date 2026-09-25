# Proposal: Codex Desktop Pooling and Limits Estimation

## Why
1. **Codex Desktop Quota & Reset Credits Pooling (#2288, #2285)**:
   - When users connect Codex Desktop to codex-lb, Codex Desktop can display quota and reset credits. However:
     - Reset credits were only read from the caller account's view rather than the aggregated pool of eligible imported accounts. Furthermore, consuming a reset credit only tried the caller account, failing when the soonest-expiring credit was on another account in the pool.
     - When an individual signed-in account became exhausted or had a different plan than the pool aggregate priority, Codex Desktop could restrict the user to Luna or report plan mismatch. Preserving the signed-in caller's account plan identity while returning genuine pooled quota windows across eligible accounts keeps Desktop active and avoids restricting users to Luna.
     - Codex Desktop / CLI makes requests to `/backend-api/wham/usage`, `/backend-api/wham/rate-limit-reset-credits/consume`, and `/backend-api/codex/usage` in addition to `/api/codex/usage`. Adding canonical aliases guarantees seamless compatibility.

2. **Weekly Limits Estimation in $ (#1793)**:
   - While the dashboard tracks estimated API cost of used tokens, users cannot easily deduce the total financial value of their 100% weekly quota limit. Tracking `limit used % / used tokens API cost in $` allows calculating the full 100% weekly limits value (`used_cost / (used_percent / 100)`), making quota scale and changes observable.

3. **Model Sources for ChatGPT OAuth in Codex Desktop (#1632)**:
   - When ChatGPT OAuth users connect Codex Desktop, models from configured Model Sources were rejected because `available_in_plans` was hardcoded to `frozenset()`, failing Desktop's client-side plan check. Parsing `available_in_plans` from source metadata and defaulting to standard plans (`free`, `plus`, `pro`, `team`, `edu`) enables ChatGPT OAuth users to select and run custom model source models.

## Changes
- **Proxy Usage & Quota API**:
  - Add route aliases on `usage_router`: `/backend-api/wham/usage`, `/backend-api/codex/usage`, `/backend-api/wham/rate-limit-reset-credits/consume`, `/backend-api/codex/rate-limit-reset-credits/consume`.
  - In `_attach_codex_usage_reset_credits`: pool available reset credits across all eligible imported accounts from `get_rate_limit_reset_credits_store()`.
  - In `codex_usage`: preserve caller's `plan_type` from `codex_usage_identity_payload` when available, while providing genuine pooled rate limit windows and availability.
  - In `codex_consume_rate_limit_reset_credit`: if `redeem_request_id` belongs to another account in the pool (or if it's the soonest expiring credit across accounts), consume via that owning account's credentials and refresh both the target and caller accounts.
- **Dashboard Weekly Pace & Limits Estimation**:
  - In `WeeklyCreditPaceResponse`: add `estimated_full_weekly_limit_cost_usd: float | None` and `used_cost_usd: float | None`.
  - In `build_weekly_credit_pace`: compute full 100% weekly limit estimated cost from `actual_used_percent` and `activity_cost_usd`.
  - In frontend `WeeklyCreditPace` / `weekly-credits-pace-card.tsx`: render estimated full weekly limits value and add localization.
- **Model Sources Catalog**:
  - In `_upstream_model_from_source`: parse `available_in_plans` from `raw["available_in_plans"]`, defaulting to all standard ChatGPT plans (`{"free", "plus", "pro", "team", "edu"}`) when omitted or empty, enabling ChatGPT OAuth users to access model sources.
