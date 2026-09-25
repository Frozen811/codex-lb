# Proposal: Populate Account Counts and Expose Availability Metrics

## Why
Operators need Prometheus alerting metrics to detect pool degradation or total account exhaustion.
While `codex_lb_accounts_total` was defined as a Gauge with a `status` label in `app/core/metrics/prometheus.py`, no component in the codebase ever updated it. Consequently, Prometheus queries such as `codex_lb_accounts_total{status="active"} < 1` cannot alert on pool exhaustion.
Furthermore, operators need a dedicated gauge `codex_lb_accounts_available` representing the count of accounts that are currently eligible and available to serve requests (i.e. active and not marked routing-unavailable).

## What Changes
- Add `codex_lb_accounts_available` gauge to `app/core/metrics/prometheus.py`.
- Configure `multiprocess_mode="livemax"` for both `codex_lb_accounts_total` and `codex_lb_accounts_available` so multiprocess deployments report unified cluster counts without redundant `pid` series.
- Add `record_account_metrics` in `app/core/metrics/prometheus.py` to record counts across all `AccountStatus` values (defaulting to 0 for unrepresented statuses) and update `codex_lb_accounts_available`.
- Update `RoutingAvailabilityCache` in `app/modules/proxy/account_cache.py` to invoke `record_account_metrics` during `refresh_from_db()`, `mark_unavailable()`, and `clear_unavailable()`.
- Register `routing_availability_cache.refresh_from_db` on `NAMESPACE_ACCOUNT_SELECTION` invalidations in `app/main.py` so account pool changes (creations, deletions, status transitions) update the metrics.

## Capabilities

### Modified Capabilities
- `proxy-runtime-observability`: Expose and continuously update `codex_lb_accounts_total` by status and `codex_lb_accounts_available`.
