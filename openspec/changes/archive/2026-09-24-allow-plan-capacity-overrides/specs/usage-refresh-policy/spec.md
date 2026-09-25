### Requirement: Plan credit capacities support registered overrides

The system MUST permit registering plan capacity overrides for any supported account plan and window (primary, secondary, monthly). When an override is registered, `capacity_for_plan` and all dependent credit calculations (including remaining credits and weekly pace projections) MUST return the registered capacity value instead of the built-in default.

#### Scenario: Calibrated Pro Lite capacity override takes precedence

- **GIVEN** a registered capacity override for `prolite` secondary window of `25000.0` credits
- **WHEN** `capacity_for_plan` is called for a `prolite` account with window `secondary`
- **THEN** the returned capacity is `25000.0`
- **AND** clearing overrides restores the default `37800.0` capacity
