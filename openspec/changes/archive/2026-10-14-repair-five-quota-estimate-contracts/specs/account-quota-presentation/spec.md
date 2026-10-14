## ADDED Requirements

### Requirement: Explicit and independent credit estimates

Absolute quota credits SHALL be identified as estimates in dashboard account and
usage responses. Default weekly estimates SHALL be independent of short-window
capacities, with Pro Lite 9000 and Pro 36000. Plan/window overrides MUST be finite,
nonnegative numeric values and SHALL affect all capacity consumers without
changing observed upstream percentages or reset timestamps.

#### Scenario: Mixed Pro pool
- **WHEN** a full Pro Lite account and exhausted Pro account have weekly observations
- **THEN** the estimated pooled weekly capacity is 45000 and remaining credits are 9000
- **AND** the pooled remaining percentage is 20 percent

#### Scenario: Override isolation
- **WHEN** the Pro weekly estimate is overridden
- **THEN** its short-window capacity and other plans remain unchanged
- **AND** NaN, infinity and boolean overrides are rejected
