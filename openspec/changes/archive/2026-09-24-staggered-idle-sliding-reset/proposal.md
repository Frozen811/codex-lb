## Why

When an opted-in account is idle (`used_percent <= limit_warmup_idle_threshold_percent`), upstream ChatGPT reports a rolling primary quota window where `reset_at` continuously slides with real time (`reset_at ≈ now + window_seconds`). The staggered idle slot calculation in `_staggered_idle_due` computes `cycle_start = reset_at - window_seconds`, which evaluates to `now`, making `elapsed ≈ 0` at every refresh poll. As a consequence, any account with a non-zero slot index (`account_index > 0`) evaluates `slot_offset <= elapsed` as false and is permanently starved.

## What Changes

- In `_staggered_idle_due`, detect when an idle account's `reset_at` is sliding with the evaluation clock (`abs((reset_at - window_seconds) - now_epoch) <= grace_seconds`).
- For sliding windows, evaluate the rolling cycle against a stable epoch-aligned cycle (`cycle_start = now_epoch - (now_epoch % window_seconds)`), preserving deterministic slot offsets across all accounts in the pool.
- Preserve the existing cycle start derived from `reset_at - window_seconds` for non-sliding (fixed) reset horizons.
- Add regression tests proving non-zero staggered idle slots fire as scheduled when `reset_at` slides with `now`.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `usage-refresh-policy`: Ensure staggered idle slots remain reachable and deterministically scheduled when upstream quota reports a sliding reset horizon.

## Impact

- Affected code: `app/modules/limit_warmup/service.py` (`_staggered_idle_due`).
- Affected tests: `tests/unit/test_limit_warmup.py`.
- No database migrations, settings, or CLI changes.
