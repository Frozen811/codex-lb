## ADDED Requirements

### Requirement: Checkout launchers prepare a ready source installation

Checkout launchers MUST select their own project directory independently of the caller's working directory and honor the frozen Python dependency lock. Normal source startup MUST prepare missing dashboard assets with the pinned frontend toolchain before invoking the owned app CLI; prerequisite/build failure MUST prevent server startup. Frontend preparation SHALL execute node-shebang build tools with the pinned Bun runtime rather than an unrelated host Node.js. CLI help MUST remain available without frontend preparation. Launchers MUST preserve user arguments and resulting CLI failure status. The Bash launcher MUST ship with Git executable permission and preserve foreground signal semantics.

#### Scenario: Invoke a source launcher from another directory

- **WHEN** an operator invokes a launcher by path from outside a checkout whose path contains spaces
- **THEN** it runs that checkout with the forwarded arguments
- **AND** the server provides readiness and bundled dashboard assets using the configured data directory

#### Scenario: Missing or incompatible frontend prerequisite

- **WHEN** normal startup needs dashboard assets but the pinned Bun toolchain is unavailable
- **THEN** startup fails with actionable prerequisite guidance and nonzero exit status
- **AND** no dashboard-less server is started

#### Scenario: CLI help or failure

- **WHEN** the operator requests help without frontend prerequisites or passes an invalid CLI argument
- **THEN** help is available without building the frontend
- **AND** invalid arguments return the CLI's nonzero failure status through the launcher
