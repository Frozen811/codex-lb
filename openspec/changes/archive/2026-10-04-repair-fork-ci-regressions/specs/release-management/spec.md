## ADDED Requirements

### Requirement: Bounded CI shards preserve complete verification

The CI pipeline MUST partition the full integration-core test selection without omissions or duplicates and MUST retain per-test timeout and stall detection. Each required shard MUST receive a finite job execution budget sufficient for the selected workload to complete. Budget exhaustion, cancellation, skipped required tests or a failed shard MUST NOT satisfy the integration-core aggregate or CI Required checks. Successful repair verification MUST identify the exact published commit SHA and completed required job results.

#### Scenario: Progressing shard exceeds its former job budget

- **WHEN** the complete shard still makes test progress at its former job deadline
- **THEN** its configured finite job budget allows completion without reducing the selected tests or disabling the test watchdog

#### Scenario: Required shard fails or is cancelled

- **WHEN** any required shard fails, times out or is cancelled
- **THEN** the integration-core aggregate and CI Required checks fail

#### Scenario: Exact-head repair is verified

- **WHEN** all required jobs for the published repair commit finish successfully
- **THEN** the verification record identifies that commit SHA and its completed CI run
