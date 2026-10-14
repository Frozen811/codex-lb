# dashboard-request-activity Specification

## Purpose

Provide locally observable dashboard request activity with explicit identity, scope and compatibility limits.

## Requirements

### Requirement: Request activity uses bounded UTC daily buckets
The authenticated dashboard SHALL expose the latest six UTC calendar months through `GET /api/dashboard/request-activity` as nonempty daily `{date, requests}` buckets. Counts SHALL combine hourly usage rollups and their exact raw complement with shared watermark partitioning, exclude warmup, and bound reads by the display interval. UTC days outside the interval MUST NOT contribute.

#### Scenario: Folded history and raw tail
- **WHEN** a display interval spans the hourly watermark
- **THEN** folded and raw counts contribute exactly once to their UTC days
- **AND** warmup and out-of-range records are excluded

### Requirement: Activity display is an optional local preference
The browser SHALL default to weekly pace and persist an alternate request heatmap mode locally. Invalid stored values SHALL restore weekly pace. The alternate view SHALL preserve usage donuts, show a seven-row UTC calendar with date/count tooltips and an intensity legend, and display loading/error/retry states. Activity SHALL only be queried while the alternate mode is active.

#### Scenario: Mode selection persists
- **WHEN** an operator selects heatmap in Appearance and reloads
- **THEN** the heatmap mode remains active on that browser
- **AND** weekly pace remains the default on other browsers
