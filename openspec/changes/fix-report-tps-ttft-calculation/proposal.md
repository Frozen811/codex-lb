# Proposal: Fix Dashboard & Report TPS / TTFT Calculation

## Problem
1. **Post-settlement latency distortion in `RequestLog.latency_ms`**:
   `_write_request_log` stamped `latency_upstream_terminal_ms` when the terminal frame was parsed before downstream delivery, settlement, and cleanup. While `record_tps_sample` used `latency_upstream_terminal_ms`, `_persist_request_log` was passed the raw `latency_ms`, persisting post-settlement latency into the database. When reports and the dashboard calculate TPS, they read `RequestLog.latency_ms`, which included the post-settlement delay and deflated TPS.
2. **Reasoning tokens deflating TPS**:
   In `app/modules/reports/repository.py` (`_daily_speed_medians_stmt`), `token_count` was computed as `RequestLog.output_tokens - func.coalesce(RequestLog.reasoning_tokens, 0)`.
   In `frontend/src/features/dashboard/components/recent-requests-table.tsx` (`formatGenerationSpeed`), `outputCount` was computed as `request.outputTokensRaw - (request.reasoningTokens ?? 0)`.
   Because the generation time denominator (`latency_ms - latency_first_token_ms`) covers both reasoning and text output generation, subtracting reasoning tokens from the numerator deflated the observed TPS for reasoning models. In contrast, `throughput_cohort.py` correctly uses `output_tokens` without subtracting reasoning tokens.

## Proposed Changes
1. **Proxy Request Log Persistence (`app/modules/proxy/_service/request_log.py`)**:
   Pass `latency_ms = latency_ms if latency_upstream_terminal_ms is None else latency_upstream_terminal_ms` when creating the `_persist_request_log` task.
2. **Reports Repository (`app/modules/reports/repository.py`)**:
   Compute `token_count = RequestLog.output_tokens` without subtracting reasoning tokens in `_daily_speed_medians_stmt`.
3. **Frontend Dashboard Table (`frontend/src/features/dashboard/components/recent-requests-table.tsx`)**:
   Compute `outputCount = request.outputTokensRaw` in `formatGenerationSpeed`.
4. **Tests**:
   - Add/update unit tests in `tests/unit/test_reports_repository.py` verifying that reasoning tokens do not reduce the TPS median.
   - Add/update tests in `tests/unit/test_proxy_http_bridge.py` or request log unit tests verifying `latency_upstream_terminal_ms` is persisted as `latency_ms`.
