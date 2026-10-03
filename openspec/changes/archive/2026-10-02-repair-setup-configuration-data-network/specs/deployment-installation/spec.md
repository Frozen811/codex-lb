## ADDED Requirements

### Requirement: Setup guidance identifies configuration discovery and precedence

The configuration guide MUST identify module-root `.env` then `.env.local` discovery, the process-only `CODEX_LB_ENV_FILE` override and its platform path separator, process environment precedence, launch-directory-relative explicit paths, and the separate CLI listener environment. It MUST distinguish application dotenv parsing from Compose env injection and Nix wrapper discovery. It MUST retain dashboard precedence over environment for dashboard-owned settings and explain ignored unknown names and missing env files.

#### Scenario: Launch a package outside its source directory

- **WHEN** an operator launches the Python package from an unrelated working directory
- **THEN** the guide supplies an explicit env-file selection example for that directory
- **AND** explains that listener CLI flags override process listener variables and dotenv files do not supply those variables

#### Scenario: Persist a dashboard override

- **WHEN** an operator sets a dashboard-owned value and later changes its environment fallback
- **THEN** the persisted dashboard value remains effective
- **AND** clearing the override restores inheritance

### Requirement: Invalid negative listener keep-alive fails before startup

The CLI MUST reject a negative `--timeout-keep-alive` or `UVICORN_TIMEOUT_KEEP_ALIVE` value before server startup with a message naming the option and its non-negative integer constraint. Zero MUST remain valid.

#### Scenario: Negative timeout from flag or environment

- **WHEN** the selected keep-alive timeout is negative
- **THEN** the CLI exits unsuccessfully before binding a listener or creating the application store

### Requirement: Backup instructions preserve paired database and encryption material

The database guide MUST distinguish a consistent SQLite snapshot from PostgreSQL/MySQL logical dumps. It MUST identify the effective DB/key/archive paths, writable-directory ownership, backup of external key paths, and restoring a matching database/key pair into an isolated rehearsal before cutover. It MUST NOT present a data-directory copy as a backup of an external SQL database or a newer binary's database downgrade as a safe rollback.

#### Scenario: Recreate or restore an installation

- **WHEN** an operator recreates an application instance or restores a backup
- **THEN** the documented steps preserve encrypted account credentials and dashboard settings using matching database/key material
- **AND** schema checks and application verification precede replacing the original store
