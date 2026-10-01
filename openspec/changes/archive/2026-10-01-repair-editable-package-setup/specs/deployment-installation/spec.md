## ADDED Requirements

### Requirement: Editable dependency setup does not compile the dashboard

Editable development installation MUST NOT require Bun or compile frontend assets during Python dependency setup. Frontend compilation SHALL remain an explicit development/workflow step. This exemption MUST NOT apply to standard distributable wheels or source distributions, which retain complete dashboard requirements and fail-closed prerequisite/output validation.

#### Scenario: CI installs backend dependencies before frontend setup

- **WHEN** uv sync installs a no-asset checkout as editable without the pinned Bun prerequisite
- **THEN** dependency setup succeeds without producing frontend assets
- **AND** a subsequent standard package build still requires complete assets or the pinned frontend toolchain

## MODIFIED Requirements

### Requirement: Python source builds include dashboard assets

Standard distributable Python source builds MUST produce wheels with dashboard HTML and non-empty referenced JavaScript/CSS assets. When complete prebuilt assets are present, the build SHALL reuse them without requiring Bun. When assets are absent, the build MUST use the frontend package's exact pinned Bun version and frozen dependency lock. Missing/wrong prerequisites, a failed frontend build or incomplete output MUST fail package creation with actionable diagnostics. The source distribution MUST include the build hook and required frontend inputs while excluding workstation dependencies, environment files and nested agent worktrees.

#### Scenario: Install from clean Git source

- **WHEN** a source checkout without prebuilt assets is installed with the pinned Bun prerequisite available
- **THEN** its wheel includes a working dashboard alongside the CLI and migrations

#### Scenario: Bun is unavailable or incompatible

- **WHEN** source assets need building and Bun is absent or differs from the pinned version
- **THEN** package creation fails with guidance identifying the required toolchain
- **AND** no dashboard-less wheel is emitted

#### Scenario: Rebuild a complete source distribution

- **WHEN** a source distribution already contains complete dashboard assets
- **THEN** its wheel can be rebuilt without Bun
- **AND** no local dependency or agent worktree state is packaged
