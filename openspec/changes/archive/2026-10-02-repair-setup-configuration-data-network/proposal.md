## Why

SETUP-02/03/04 lack independent configuration, persistence and endpoint evidence. Current operator instructions misidentify env-file discovery, imply that a data-directory copy backs up every database, and expose a host-only database URL without explaining container addressing.

## What Changes

- Document actual env-file discovery, ordered precedence, launch-mode differences and validation failures.
- Reject negative CLI keep-alive timeouts before starting the server.
- Provide backend-specific backup/restore guidance, paired database/key retention and writable-storage requirements.
- Document bind addresses versus client endpoints, callback port separation and host/container database addressing.
- Rehearse isolated SQLite, PostgreSQL and MySQL persistence/restore paths and record bounded evidence in issues-check.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: setup configuration and database/key backup instructions; invalid keep-alive rejection.
- `deployment-networking`: explicit endpoint/addressing matrix and failure diagnostics.

## Impact

`app/cli.py`, CLI/env-file and process regression tests, `.env.example`, `docs/configuration.md`, `docs/database.md`, `docs/deployment/remote.md`, the existing Docker storage paragraph, owning OpenSpec requirements/context and `issues-check.md`. Existing local fixes remain intact. No new settings, dependencies, schema revisions or release changes.
