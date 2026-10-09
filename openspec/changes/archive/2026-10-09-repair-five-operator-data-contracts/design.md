## Context

The existing CLI scans provider fields anywhere in JSONL, repeats SQLite counts and rescans the home after writes. Online Alembic execution belongs to its migration context. Existing facet indexes and the SCIM/overflow merge are published history and must not be rewritten.

## Goals / Non-Goals

Implement bounded metadata planning and operator diagnostics, and verify existing facet/merge behavior. No automatic repair, live-home operation, rewritten migration history or new database setting.

## Decisions

- Read at most 64 KiB of each JSONL header. Recognize the canonical first session_meta or leading legacy provider records, then copy the remaining bytes opaquely when rewriting. Reject ambiguous or incomplete initial metadata. Preserve session selection and existing SQLite fallback.
- Plan SQLite from one grouped provider-count query per eligible database; verify planned rows after mutation and derive whole-home counts from the cached plan. Keep SQL identifiers restricted to known columns.
- Report phase progress through a typed callback; CLI JSON progress is opt-in on stderr. Broken pipes disable progress without interrupting data ownership. Backup failures and partial rewrites report retained paths.
- Wrap Alembic's migration step iterable only for online execution, restoring the original callable in finally. Each wrapper delegates the original step function, logs start/executed/failed and preserves the original exception. No SQL, URL, revision description or exception text enters progress records. Executed is not committed.
- Unknown revision errors gain conditional guidance only. Stamp preconditions are operator checks; no automated stamping or relaxed acceptance is introduced.
- Verify the merge revision at its historical identity, while asserting the current head descends from it. Exercise both actual populated parents and downgrade/re-upgrade; never stamp a fake branch schema.
- Verify the facet migration and SQLite API semantics plus SQL compilation for other dialects where no live service exists. External engines remain explicit residuals.

## Risks / Trade-offs

- Closed clients are required for multi-file retag; backups support manual recovery, not a cross-store transaction.
- Fixed header bounds deliberately reject unusually large metadata; opaque transcript growth does not increase planning reads.
- Alembic iterator wrapping touches a private callback; targeted success/failure/downgrade/no-op restoration tests pin compatibility with the installed version.
- SQLite evidence cannot certify PostgreSQL/MySQL runtime or published artifacts. Existing unrelated dirty changes remain separately owned.
