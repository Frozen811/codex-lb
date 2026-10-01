## ADDED Requirements

### Requirement: Python source builds include dashboard assets

Python source builds MUST produce wheels with dashboard HTML and non-empty referenced JavaScript/CSS assets. When complete prebuilt assets are present, the build SHALL reuse them without requiring Bun. When assets are absent, the build MUST use the frontend package's exact pinned Bun version and frozen dependency lock. Missing/wrong prerequisites, a failed frontend build or incomplete output MUST fail package creation with actionable diagnostics. The source distribution MUST include the build hook and required frontend inputs while excluding workstation dependencies, environment files and nested agent worktrees.

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

### Requirement: Python installation instructions select a known fork channel

Fork Python installation instructions MUST distinguish release artifacts, pinned Git source and upstream index commands. Historical artifacts MUST disclose metadata/runtime/source differences and MUST NOT claim newer checkout fixes. Documented fork wheel, sdist and uv tool installs MUST start outside the repository using isolated audit storage, provide readiness and dashboard assets, expose migration commands and retain configured data/key storage across an update. Source-install prerequisites SHALL be explicit.

#### Scenario: Bare upstream index command

- **WHEN** installation guidance discusses bare `uvx codex-lb` or `pip install codex-lb`
- **THEN** it identifies that those commands select upstream rather than this fork

#### Scenario: Historical fork package installation

- **WHEN** an operator selects the documented historical fork release package
- **THEN** instructions identify its actual artifact identity and limitations
- **AND** audit results distinguish successful installation from proof of newer published fixes
