# Tasks: fix-report-tps-ttft-calculation

- [x] 1. Proxy Request Log Persistence
  - [x] 1.1 In `app/modules/proxy/_service/request_log.py`, pass `latency_ms = latency_ms if latency_upstream_terminal_ms is None else latency_upstream_terminal_ms` to `_persist_request_log`.
- [x] 2. Reports Repository TPS Calculation
  - [x] 2.1 In `app/modules/reports/repository.py`, change `token_count` to `RequestLog.output_tokens` in `_daily_speed_medians_stmt`.
- [x] 3. Dashboard Recent Requests Table
  - [x] 3.1 In `frontend/src/features/dashboard/components/recent-requests-table.tsx`, change `outputCount` to `request.outputTokensRaw` in `formatGenerationSpeed`.
- [x] 4. Tests & Verification
  - [x] 4.1 Update `tests/unit/test_reports_repository.py` with a test verifying reasoning tokens do not reduce the TPS median.
  - [x] 4.2 Verify existing tests pass and lint/type checks pass.
