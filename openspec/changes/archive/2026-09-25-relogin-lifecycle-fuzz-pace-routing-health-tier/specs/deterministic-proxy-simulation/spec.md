# deterministic-proxy-simulation Specification Delta

## ADDED Requirements

### Requirement: Property-based balancer state fuzzing and invariant preservation

The test framework SHALL provide property-based fuzz testing using `hypothesis` covering account selection and load balancer state transitions. Fuzzing MUST verify that across arbitrary permutations of account states (including extreme usage values, negative remaining credits, floating point boundaries, and varied health tiers), core balancer invariants hold without raising unhandled exceptions or violating exclusion sets.

#### Scenario: Fuzz inputs preserve exclusion invariants
- **GIVEN** an arbitrary generated pool of account states
- **AND** a subset of account IDs marked as excluded
- **WHEN** account selection runs
- **THEN** no excluded account ID is ever returned

#### Scenario: Fuzz inputs preserve inactive state invariants
- **GIVEN** an arbitrary generated pool of account states with varied statuses
- **WHEN** normal account selection runs without recovery probing
- **THEN** no account with status other than `ACTIVE` is ever selected
