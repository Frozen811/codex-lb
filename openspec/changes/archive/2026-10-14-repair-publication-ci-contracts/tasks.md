## 1. Replay compatibility

- [x] 1.1 Guard additive timing DDL with schema inspection and verify both missing-column and precreated-column roundtrips.
- [x] 1.2 Expose restored-store reader stderr on failure and verify the CLI paired-restore test retains its assertions.

## 2. Verification and specification

- [x] 2.1 Run the failing SQLite startup, metadata-bootstrap, lifecycle and replay regression paths and record exact results plus hosted backend limits.
- [x] 2.2 Sync the replay requirement and context, run strict change/canonical validation and the migration topology/static checks, and archive after local verification.

## 3. Bridge and facet regression contracts

- [x] 3.1 Preserve parent alias idle retention while retaining child caps, and verify the parent alias plus child retention tests.
- [x] 3.2 Bring API-key isolation and upstream facet fixtures into the current schemas, add a bounded SQLite missing-NULL preprobe, and preserve the existing SQLite operation ceiling and PostgreSQL facet checks.

## 4. Dependency audit repair

- [x] 4.1 Update the pinned rustls patch and verify Rust formatting, Clippy, workspace tests and release build; keep hosted advisory results distinct from local checks.
