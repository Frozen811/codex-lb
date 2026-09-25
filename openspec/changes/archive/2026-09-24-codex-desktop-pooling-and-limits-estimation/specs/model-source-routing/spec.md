# model-source-routing Delta Specification

## Requirements

### Requirement: Model sources declare plan availability for ChatGPT OAuth consumers

When constructing upstream model descriptors from configured Model Sources, the catalog builder SHALL populate `available_in_plans` from the source model's metadata when present, and SHALL default to all standard ChatGPT plan types (`free`, `plus`, `pro`, `team`, `edu`) when omitted or empty, enabling ChatGPT OAuth users in Codex Desktop to access model source models.

#### Scenario: Custom model source defaults to standard ChatGPT plans
- **GIVEN** an enabled model source with no explicit plan restrictions in metadata
- **WHEN** the model catalog is projected for Codex clients
- **THEN** each model entry includes standard ChatGPT plans in `available_in_plans`
- **AND** Codex Desktop client-side plan validation allows the model for ChatGPT accounts
