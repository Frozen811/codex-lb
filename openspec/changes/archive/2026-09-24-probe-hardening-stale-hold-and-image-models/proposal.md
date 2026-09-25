# Change: Force Probe Payload Hardening, Stale Hold Recovery, and GPT Image 2.5 Support

## Why
1. **Force Probe Unsupported Fields and Detached Instances (#2410)**:
   - Force Probe in `app/modules/accounts/service.py` sends `max_output_tokens` directly to `/backend-api/codex/responses` without filtering unsupported upstream fields (`_UNSUPPORTED_UPSTREAM_FIELDS`). Upstream endpoints reject `max_output_tokens` with HTTP 400.
   - In `LoadBalancer.record_probe_result`, ORM instances `account`, `primary_entry`, and `effective_secondary_entry` are accessed outside the repository session without cloning, raising `sqlalchemy.orm.exc.DetachedInstanceError` and preventing successful probe settlement.
2. **Recover Stale Holds After Verified Matching Probes (#2327)**:
   - When an account was previously marked `RATE_LIMITED` with a persisted `blocked_at` / `reset_at`, a server restart wipes in-memory cooldown evidence while preserving the persisted deadline.
   - Even when upstream accepts the model again and an operator probe returns HTTP 200 with fresh usage showing available quota (<100%), `UsageUpdater._apply_usage_quota` rejects recovering the account because `now < cooldown_deadline`.
   - Verified successful operator probes with available quota must recover stale rate-limit holds to `ACTIVE`.
3. **Images API GPT Image 2.5 Support (#2304)**:
   - The `/v1/images/generations` and `/v1/images/edits` endpoints reject `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` with HTTP 400 because `_GPT_IMAGE_2_MODELS` in `app/core/openai/images.py` only permits `gpt-image-2`.
   - Upstream Responses `image_generation` natively supports these models; adding them to `_GPT_IMAGE_2_MODELS` enables public parity while keeping the default model `gpt-image-2`.

## What Changes
1. **Force Probe Sanitization & Snapshot Cloning (`app/modules/accounts/service.py`, `app/modules/proxy/load_balancer.py`)**:
   - In `_send_probe_request`, pass the probe payload through `_strip_compact_unsupported_fields` to ensure unsupported upstream fields such as `max_output_tokens` are stripped.
   - In `LoadBalancer.record_probe_result`, clone `account`, `primary_entry`, and `effective_secondary_entry` with `_clone_account` and `clone_row` inside the repository context before exiting.
   - Consolidate redundant imports in `load_balancer.py` to maintain line count `<= 3021`.
2. **Stale Hold Recovery on Verified Probe (`app/modules/usage/updater.py`, `app/modules/accounts/service.py`)**:
   - In `AccountsService.probe_account`, pass `probe_verified=(200 <= probe_status < 300)` to `force_refresh_result`.
   - In `UsageUpdater._apply_usage_quota`, allow verified probe refreshes to recover `RATE_LIMITED` accounts with available quota, clearing `blocked_at`, `reset_at`, and setting status to `ACTIVE`.
3. **Images API Model Allowlist (`app/core/openai/images.py`)**:
   - Add `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` to `_GPT_IMAGE_2_MODELS`.
   - Preserve default `gpt-image-2` behavior and per-model parameter matrix.

## Capabilities

### Modified Capabilities
- `usage-refresh-policy`: Require stripping unsupported fields in probe payloads and recovering stale holds when an operator probe is verified successful with available quota.
- `images-api-compat`: Add `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` to the allowed `gpt-image-2` family models.

## Impact
- `app/modules/accounts/service.py`
- `app/modules/usage/updater.py`
- `app/modules/proxy/load_balancer.py`
- `app/core/openai/images.py`
- `tests/unit/test_accounts_service_probe.py`
- `tests/unit/test_load_balancer.py`
- `tests/unit/test_usage.py`
- `tests/unit/test_images_schemas.py`
- `tests/integration/test_proxy_images.py`
