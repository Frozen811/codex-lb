## 1. Implementation

- [x] 1.1 In `app/core/metrics/prometheus.py`, declare `accounts_available` gauge, set `multiprocess_mode="livemax"` on `accounts_total` and `accounts_available`, and implement `record_account_metrics`.
- [x] 1.2 In `app/modules/proxy/account_cache.py`, add `_update_metrics` to `RoutingAvailabilityCache` and call it on `refresh_from_db()`, `mark_unavailable()`, `clear_unavailable()`, and `reset()`.
- [x] 1.3 In `app/main.py`, register `routing_availability_cache.refresh_from_db` on `NAMESPACE_ACCOUNT_SELECTION` invalidations.

## 2. Regression Coverage

- [x] 2.1 Add unit tests in `tests/unit/test_account_metrics.py` verifying `record_account_metrics` and `RoutingAvailabilityCache` integration for `codex_lb_accounts_total` and `codex_lb_accounts_available`.

## 3. Validation

- [x] 3.1 Run unit tests with pytest.
- [x] 3.2 Run migration topology checks.
