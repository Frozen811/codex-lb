# Change: subagent-ttl-observation-windows-images-fanout-ci-labels

## Why
This change addresses Batch 40 (Issues #1307, #1080, #620, #2314):
1. **Issue #1307 (subagent prompt-cache affinity TTL)**: OpenCode and Codex child tasks (subagents) identify themselves with headers like `x-parent-session-id`, `x-openai-subagent`, and `x-codex-parent-thread-id`. Currently, their `PROMPT_CACHE` affinity inherits the parent's 3600s TTL, which holds stream leases for up to an hour after subagent completion and exhausts account stream capacity. Bounding subagent prompt-cache affinity to 300s (5 minutes) frees leases rapidly after child tasks finish.
2. **Issue #1080 (configurable longer observation windows for API key usage)**: The API keys usage endpoint currently exposes only a 7-day window (`/usage-7d`). Operators managing multiple keys need longer-term visibility (14d, 30d, up to 90d) for billing and trend analysis. We add `GET /api/api-keys/{key_id}/usage` with a configurable `days` query parameter (1-90, default 7), add `days` support to `/trends`, and maintain `/usage-7d` as a backward-compatible alias.
3. **Issue #620 (complete deferred Images API fan-out and observability tasks)**: The OpenAI-compatible `/v1/images/*` implementation previously hard-rejected `n > 1` because client-side fan-out was not implemented. We implement non-streaming fan-out up to `MAX_IMAGE_FANOUT = 10` using `asyncio.gather`, aggregate resulting image data and sum token usage, reject streaming with `n > 1`, and update observability logs.
4. **Issue #2314 (reconcile issue and PR status-label ownership and lifecycle)**: When a reporter or user responds to an issue or PR marked `needs-info`, the `needs-info` and `stale` labels should be automatically reconciled (removed) and `triage` / `awaiting-review` added so issues don't remain stuck waiting on reporters who already answered.

## What Changes
- `app/modules/proxy/affinity.py`:
  - Define `SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS = 300`.
  - Add detection for subagent headers (`x-parent-session-id`, `x-openai-subagent`, `x-codex-parent-thread-id`).
  - Calculate effective prompt-cache TTL as `min(configured_ttl, SUBAGENT_PROMPT_CACHE_MAX_AGE_SECONDS)` for subagents.
- `app/modules/proxy/_service/compact.py`:
  - Apply effective prompt-cache TTL for subagents.
- `app/modules/api_keys/schemas.py`:
  - Add `ApiKeyUsageResponse` model with `days` field.
- `app/modules/api_keys/service.py`:
  - Add `get_key_usage(self, key_id: str, days: int = 7)`.
  - Add `days: int = 7` parameter to `get_key_trends`.
- `app/modules/api_keys/api.py`:
  - Add `GET /api/api-keys/{key_id}/usage` accepting `days: int = Query(default=7, ge=1, le=90)`.
  - Update `GET /api/api-keys/{key_id}/trends` to accept `days: int = Query(default=7, ge=1, le=90)`.
  - Preserve `GET /api/api-keys/{key_id}/usage-7d`.
- `app/core/openai/images.py`:
  - Define `MAX_IMAGE_FANOUT = 10`.
  - Accept `1 <= n <= 10` for non-streaming image generation; reject `n > 1` if `stream=True`.
- `app/modules/proxy/images_service.py` & `app/modules/proxy/api.py`:
  - Implement concurrent fan-out for `n > 1` non-streaming image generations using `asyncio.gather`.
  - Aggregate image data array and sum token usage.
- `app/modules/proxy/images_observability.py`:
  - Record fan-out count in log when `fanout > 1`.
- `.github/workflows/reconcile-issue-activity.yml`:
  - Automated label reconciliation when reporter comments on `needs-info` issue or PR.
- Unit and integration tests for all four areas.
