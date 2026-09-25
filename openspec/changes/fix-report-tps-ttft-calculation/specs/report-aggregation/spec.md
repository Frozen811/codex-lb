# report-aggregation Specification Delta

## Requirements
### Requirement: Bounded speed work
Exact speed medians SHALL only run for date windows of at most seven days. Longer windows SHALL retain zero-valued numeric speed fields for compatibility, return `speedMetricsAvailable=false` and the maximum supported speed-window size and SHALL NOT execute median SQL. The dashboard SHALL explain the omission and hide unavailable speed charts. Daily TPS medians SHALL calculate throughput using total output tokens over generation span without subtracting reasoning tokens from output tokens.

#### Scenario: TPS calculation with reasoning tokens
- **GIVEN** request logs containing reasoning tokens and output tokens
- **WHEN** daily speed medians are aggregated
- **THEN** TPS calculation SHALL use `output_tokens / (latency_ms - latency_first_token_ms)` without deducting reasoning tokens from the token count
