# Tasks: Force Probe Payload Hardening, Stale Hold Recovery, and GPT Image 2.5 Support

## 1. Force Probe Payload & Settlement Hardening (#2410)
- [x] 1.1 Strip unsupported fields in `AccountsService._send_probe_request` via `_strip_compact_unsupported_fields`.
- [x] 1.2 In `LoadBalancer.record_probe_result`, clone `account`, `primary_entry`, and `effective_secondary_entry` with `_clone_account` and `clone_row` inside the repo context.
- [x] 1.3 Consolidate sticky selection imports in `load_balancer.py` to maintain line count `<= 3021`.
- [x] 1.4 Update `tests/unit/test_accounts_service_probe.py` to verify `max_output_tokens` is stripped.
- [x] 1.5 Add regression test for `LoadBalancer.record_probe_result` with detached ORM entities.

## 2. Stale Hold Recovery on Verified Probe (#2327)
- [x] 2.1 Pass `probe_verified=(200 <= probe_status < 300)` from `AccountsService.probe_account` to `force_refresh_result`.
- [x] 2.2 In `UsageUpdater._apply_usage_quota`, permit verified probe refreshes to recover `RATE_LIMITED` accounts with available quota, clearing `blocked_at`, `reset_at`, and restoring status to `ACTIVE`.
- [x] 2.3 Add unit tests verifying verified probe recovery of stale rate limits.

## 3. Images API GPT Image 2.5 Support (#2304)
- [x] 3.1 Add `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` to `_GPT_IMAGE_2_MODELS` in `app/core/openai/images.py`.
- [x] 3.2 Add unit tests in `tests/unit/test_images_schemas.py` and integration tests in `tests/integration/test_proxy_images.py`.

## 4. Verification & Sync
- [x] 4.1 Run test suite (`pytest`) for affected modules.
- [x] 4.2 Run linters (`ruff check app tests`).
- [x] 4.3 Validate OpenSpec specs (`openspec validate --specs`).
