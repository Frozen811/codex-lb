## ADDED Requirements

### Requirement: Architecture diagnostics use portable paths

Architecture-check diagnostics MUST render repository-relative paths with forward slashes on every supported operating system. Paths outside the repository MUST retain their absolute identity with forward slashes. This formatting MUST NOT suppress independently evaluable checks or change ratchets.

#### Scenario: Windows diagnostic identifies a source or threshold failure

- **WHEN** the checker reports a source parse failure or invalid threshold definition on Windows
- **THEN** it reports the same repository-relative forward-slash path as on Linux
- **AND** it continues all independently evaluable checks
