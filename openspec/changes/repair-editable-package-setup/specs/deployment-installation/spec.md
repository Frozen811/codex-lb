## ADDED Requirements

### Requirement: Editable dependency setup does not compile the dashboard

Editable development installation MUST NOT require Bun or compile frontend assets during Python dependency setup. Frontend compilation SHALL remain an explicit development/workflow step. This exemption MUST NOT apply to standard distributable wheels or source distributions, which retain complete dashboard requirements and fail-closed prerequisite/output validation.

#### Scenario: CI installs backend dependencies before frontend setup

- **WHEN** uv sync installs a no-asset checkout as editable without the pinned Bun prerequisite
- **THEN** dependency setup succeeds without producing frontend assets
- **AND** a subsequent standard package build still requires complete assets or the pinned frontend toolchain
