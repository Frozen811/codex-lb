## ADDED Requirements

### Requirement: Helm startup probe timing is configurable
The chart MUST expose integer initial delay, period, timeout and failure threshold values while preserving defaults of 5, 2, 1 and 30 seconds or attempts respectively. Initial delay MUST be nonnegative and the other values MUST be positive. The startup probe MUST use /health/startup on named port http and successThreshold MUST equal 1. Startup overrides MUST NOT alter readiness or liveness probes.

#### Scenario: Default and customized startup
- **WHEN** an operator renders the chart with defaults or individual timing overrides
- **THEN** the application startup probe reflects the selected timing with its fixed handler

#### Scenario: Invalid probe values
- **WHEN** an operator supplies null, fractional, boolean or out-of-range timing values or a success threshold other than 1
- **THEN** Helm rendering fails validation

