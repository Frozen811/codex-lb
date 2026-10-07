## ADDED Requirements

### Requirement: Historical monthly quota uses the ingestion classification
Account summaries SHALL classify a historical primary-slot quota as monthly only when its duration is within 40320 through 46080 minutes inclusive and its secondary observation is absent or has zero duration. This classification SHALL apply independently of plan. A positive or unknown-duration secondary observation SHALL preserve the original primary and secondary windows. Monthly percentages and reset metadata SHALL remain available without an estimated monthly capacity. Team monthly capacity and remaining credits SHALL be null unless an explicit measured override is configured. Newer valid short or weekly observations SHALL supersede stale monthly history for plans without a monthly capacity.

#### Scenario: Historical monthly quota with a placeholder
- **WHEN** a Free or Team account has a historical primary observation of 43800 minutes and an absent or zero-duration secondary observation
- **THEN** its summary exposes only the monthly quota with its observed percentage and duration

#### Scenario: Out-of-band or ambiguous observation
- **WHEN** a primary duration is 40319 or 46081 minutes, or a monthly-duration primary has a positive or unknown-duration secondary observation
- **THEN** its original windows remain available without monthly-only reclassification

#### Scenario: Team monthly capacity is unknown
- **WHEN** a Team account reports monthly quota and no explicit measured monthly override exists
- **THEN** the summary preserves monthly percentages and reset metadata while monthly capacity and remaining credits are null

#### Scenario: Team transitions to short and weekly quota
- **WHEN** a Team account has short or weekly observations newer than its monthly history
- **THEN** the summary exposes the newer windows and omits the stale monthly quota

#### Scenario: Historical Free monthly exhaustion remains visible
- **WHEN** a Free account has a lone historical primary-slot monthly quota at 100 percent used
- **THEN** its summary exposes Monthly 0 percent remaining and derives quota exhaustion from that monthly observation
