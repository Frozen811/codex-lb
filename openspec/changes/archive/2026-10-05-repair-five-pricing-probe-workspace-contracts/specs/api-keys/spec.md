## ADDED Requirements

### Requirement: Effective Ultrafast tier settles exact monetary limits
API-key cost settlement MUST price the effective upstream response tier, including disjoint ordinary input, cached reads, cache writes and output at the applicable context rates. Settlement MUST avoid losing integral microdollars through a floating-point USD roundtrip and MUST retain truncation of genuine fractional microdollars. Repeated finalization MUST remain idempotent.

#### Scenario: Ultrafast downgrade
- **WHEN** a request asks for Ultrafast but upstream confirms default
- **THEN** logs and cost-limit settlement use the default rates

#### Scenario: Exact charge and subsequent admission
- **WHEN** upstream confirms Ultrafast usage that exhausts a key's cost limit
- **THEN** its stored cost and settled microdollars agree
- **AND** the next request is refused before dispatch

#### Scenario: Mixed cached input
- **WHEN** usage reports cached reads and writes
- **THEN** each input token is charged once at its applicable rate

