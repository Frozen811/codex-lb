## ADDED Requirements

### Requirement: Container scan enforcement precedes report publication

Container CI MUST enforce its existing fixed HIGH/CRITICAL vulnerability policy before publishing its SARIF report to GitHub Security. Scan evidence MUST be retained as a workflow artifact when report generation succeeds, including when the vulnerability gate fails. Remote publication failures MUST remain visible failures under the existing trusted-event publication condition and MUST NOT prevent the preceding vulnerability gate from executing.

#### Scenario: Remote report publication fails
- **WHEN** GitHub Security rejects or fails a SARIF upload
- **THEN** the vulnerability gate has already executed
- **AND** the generated SARIF report is available as a workflow artifact
- **AND** the eligible upload remains a failed step

#### Scenario: Fixed high-severity vulnerability is found
- **WHEN** Trivy finds a fixed HIGH or CRITICAL vulnerability outside the existing ignore policy
- **THEN** the vulnerability gate fails the container job
- **AND** report generation and artifact retention are still attempted
