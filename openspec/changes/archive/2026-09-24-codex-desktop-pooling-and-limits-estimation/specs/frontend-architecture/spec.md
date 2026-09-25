# frontend-architecture Delta Specification

## Requirements

### Requirement: Dashboard displays estimated dollar value of full weekly limits

The dashboard weekly pace card SHALL expose an estimated financial value in USD for the full (100%) weekly limits, derived from the actual weekly limit used percentage and the estimated API cost of used tokens.

#### Scenario: Weekly pace card displays estimated full weekly limits value
- **GIVEN** a non-zero weekly quota used percentage
- **AND** a non-zero estimated token cost in USD
- **WHEN** the weekly pace card renders
- **THEN** it displays the estimated full 100% weekly limit value in USD
- **AND** it shows the current cost used and percentage as context
