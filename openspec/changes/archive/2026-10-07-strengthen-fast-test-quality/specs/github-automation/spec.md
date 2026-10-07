## ADDED Requirements

### Requirement: Fast mandatory checks preserve precise asynchronous invariants

The mandatory test suite SHALL retain its existing selection and property-test
budgets. It SHALL test startup errors on both sides of the production probe
deadline using virtual time, including cancellation cleanup. Dashboard browser
checks SHALL reject document overflow in observed resize frames and verify
settled containment after DOM and font readiness without retrying failed
geometry assertions. Reservation regressions SHALL synchronize competing
operations in one database with independently owned sessions and bounded task
cleanup, and SHALL prove quota admission and exactly-once settlement or release.

#### Scenario: Startup error crosses the probe deadline

- **WHEN** an upstream error arrives just before or after the startup deadline
- **THEN** virtual-time checks distinguish startup failure from streamed failure
- **AND** cancellation leaves no owned pending task or timer

#### Scenario: Multiple callers contend for one reservation or quota

- **WHEN** synchronized callers compete using independent database sessions
- **THEN** admission does not exceed quota and settlement or release changes accounting once
- **AND** no competing task remains running after test completion

### Requirement: Extended properties supplement the mandatory pipeline

A separate read-only GitHub workflow SHALL run selected properties nightly and
on manual dispatch with at least 500 generated examples per selected property.
Normal CI SHALL retain their existing budgets and explicit edge examples.
Extended runs SHALL record the seed and commit, accept a replay seed, and upload
seed metadata, JUnit results and Hypothesis failure evidence even after failure.
The main CI required aggregate MUST NOT depend on this additional workflow.

#### Scenario: A generated regression requires reproduction

- **WHEN** the extended property workflow fails
- **THEN** its artifacts identify the commit and seed needed for reproduction
- **AND** manual dispatch accepts that seed without reducing the selected budgets
