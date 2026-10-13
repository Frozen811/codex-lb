## ADDED Requirements

### Requirement: Contributor guidance states bounded completion and verification

Repository agent instructions MUST state ownership of the requested scope, preservation of unrelated work, autonomous completion of authorized implementation and validation, and calibration of testing to the changed subsystem. They MUST identify OpenSpec as the behavior source of truth, preserve existing contributor and merge gates, require disposable test storage before application imports, and require regression coverage of affected externally observable request transports. They MUST distinguish local verification from publication and deployment authority.

#### Scenario: Scoped behavior repair
- **WHEN** an agent follows the repository instructions for a behavior change
- **THEN** it creates the required OpenSpec artifacts before implementation, validates the affected behavior and synchronizes verified specs
- **AND** it preserves unrelated work and does not substitute local tests for cloud merge gates

#### Scenario: Affected request paths and isolated storage
- **WHEN** a change affects HTTP, WebSocket or HTTP-bridge behavior
- **THEN** the instructions require regression coverage of the affected product paths and applicable aliases
- **AND** test database configuration precedes imports that initialize application storage
