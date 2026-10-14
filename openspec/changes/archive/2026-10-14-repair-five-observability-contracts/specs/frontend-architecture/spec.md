## ADDED Requirements

### Requirement: Request-log upstream selection is URL-backed and historically identifiable
The dashboard SHALL expose an Upstream multiselect when multiple observed upstreams exist or a selection is active. Stable IDs SHALL persist in the URL, reset SHALL clear them and reset pagination, and deleted sources SHALL have localized fallbacks. Duplicate current names SHALL be disambiguated with source IDs. Source-routed rows SHALL have compact badges and details SHALL retain full source ID/kind. Older API responses without upstream options SHALL remain usable.

#### Scenario: Historical source selection survives reload
- **WHEN** a deleted model source is selected and the page reloads
- **THEN** its stable upstream filter and localized identity are retained
- **AND** resetting filters removes the selection
