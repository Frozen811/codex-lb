## MODIFIED Requirements

### Requirement: Bounded speed work
Exact speed medians SHALL only run for date windows of at most seven days. Longer windows SHALL retain zero-valued numeric speed fields for compatibility, return `speedMetricsAvailable=false` and the maximum supported speed-window size and SHALL NOT execute median SQL. The dashboard SHALL explain the omission and hide unavailable speed charts.

#### Scenario: Ninety-day report
- **WHEN** an operator requests a 90-day report
- **THEN** the report SHALL return aggregate totals without running raw median calculations
- **AND** the page SHALL state that speed metrics require a window of seven days or less

#### Scenario: Dense seven-day report
- **GIVEN** a seven-day request history with valid speed evidence
- **WHEN** the report is loaded through the dashboard API before or after historical totals are folded
- **THEN** totals and exact daily speed medians SHALL agree
- **AND** folding totals SHALL NOT suppress short-window speed samples still present in raw history
