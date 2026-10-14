## Overview

codex-lb is designed to be SQLite-first for simple local usage and container defaults. SQLite-specific resilience behavior (integrity checks, WAL tuning, recovery tooling) remains valuable for the default mode.

For higher concurrency or infrastructure-managed deployments, PostgreSQL support is enabled through SQLAlchemy async URLs using `asyncpg`.

## Decisions

- Keep SQLite as default to preserve zero-config startup.
- Accept PostgreSQL through `CODEX_LB_DATABASE_URL` only; no new configuration key aliases.
- Keep SQLite-specific recovery tooling SQLite-only; PostgreSQL operations should use PostgreSQL-native backup/recovery practices.
- Default SQLite startup validation to `quick` so normal boots stay fast while operators can still opt into `full` or `off`.

## Operational Notes

- SQLite default URL: `sqlite+aiosqlite:///~/.codex-lb/store.db`
- SQLite startup check mode: `CODEX_LB_DATABASE_SQLITE_STARTUP_CHECK_MODE=quick|full|off` (default `quick`)
- PostgreSQL example URL: `postgresql+asyncpg://codex_lb:codex_lb@127.0.0.1:5432/codex_lb`
- Pool sizing (`database_pool_size`, `database_max_overflow`) applies to PostgreSQL engine creation; the pool checkout timeout (30 s) and connection recycle window (1800 s) are fixed constants in `app/db/session.py` (issue #1340 phase 3).
- The background/request-adjacent DB engine always derives its pool sizing from `database_pool_size` and `database_max_overflow`; it isolates background-task checkouts rather than being sized independently.
- A supported application replica runs one worker with two independently pooled PostgreSQL engine roles (request path and background tasks), so its maximum application connection count is `2 * (database_pool_size + database_max_overflow)`. The owned CLI pins one Uvicorn worker even if `WEB_CONCURRENCY` is present; custom multi-worker launchers are unsupported.

## Example

Use PostgreSQL while keeping all other defaults:

```bash
CODEX_LB_DATABASE_URL=postgresql+asyncpg://codex_lb:codex_lb@127.0.0.1:5432/codex_lb codex-lb
```

Use SQLite with explicit full startup validation:

```bash
CODEX_LB_DATABASE_SQLITE_STARTUP_CHECK_MODE=full codex-lb
```

## SQLite teardown completion grace

A file-backed SQLite worker can finish rollback or close while the event loop is delayed and has not delivered the completion callbacks. The initial teardown bound therefore begins a separate bounded opportunity to observe successful task completion. Only success avoids reclamation; failed, cancelled or still-pending teardown retains the pre-teardown connection snapshot, session fence and tracked cleanup owner. The existing 0.75-second grace can add that delay before a genuine wedge is reclaimed; it is not a measured optimum.

The caller owns teardown during both the initial wait and grace. Only reclamation registers abandoned work in the database shutdown registry, so a concurrent `close_db()` can finish during either observation window. Grace extends that existing exposure by up to 0.75 seconds. The application's separate request and leader-release drain results still govern whether shutdown may be marked clean.

For example, a native rollback may finish while the loop is blocked across the initial bound. Grace observes its success, normal session close proceeds and a second writer can commit. Real file-SQLite regression checks reproduce this ordering on asyncio and uvloop; disabling grace restores false interruption. This demonstrates a reachable ordering failure, not the cause or duration of historical production stalls.

Warnings distinguish observed completion, attempted reclamation and failed cleanup. Elapsed time at the initial bound is not an event-loop lag measurement, and a failed invalidation does not prove a permanent writer hold. No database migration, pool change or operator setting is required. The [owning requirement](spec.md#requirement-a-completed-sqlite-teardown-is-never-reclaimed) defines the completion and cleanup contract.

The invalidation warning covers exceptions raised by `connection.invalidate()`. SQLAlchemy 2.0.52 catches ordinary driver-close exceptions inside `Pool._close_connection` and logs them at ERROR, so those failures retain the pool's diagnostic owner. Finalization can also run for a task already terminal during grace; its message reports completion without claiming that the task finished after reclamation.


## Local SQLite admission and cancelled cleanup

The [database-backends requirements](spec.md) cover shared local write admission. Its reentrancy belongs to the current asyncio task. Context copied into a child preserves ambient data but does not transfer lock ownership: create a child while holding admission only if the parent can leave before awaiting that child to write. Same-task nested repository calls remain supported.

Authentication attempt writes, OAuth flow persistence, fingerprint verification and lease writes use this admission to avoid spending the native busy timeout against an already admitted local writer. OAuth/fingerprint/lease sessions are scoped inside admission, so rollback and close run before its release. OAuth network exchange and password verification run outside it. For example, a paused SQLite writer can delay an OAuth flow record; releasing its transaction admits persistence and returns a pending browser flow, rather than a lock-error HTTP 500.

Lease writes still judge expiry using the database execution clock after waiting. Admission does not grant a new TTL to an expired lease. PostgreSQL and in-memory SQLite retain their concurrency behavior, and external SQLite processes still require the existing bounded lock retry policy.

Reclamation registers both the abandoned teardown and its connection-cleanup task before waiting. Caller cancellation is deferred until interruption/invalidation and late-close callback registration finish. A failed interrupt does not prove a permanent lock; invalidation is still attempted and its failure is reported. The cleanup registry remains drainable at shutdown. No process restart, production repair or guaranteed native-driver recovery follows from these local checks.


## Traceback-retained SQLite RETURNING cursors (2026-10-14)

The [retained-cursor teardown requirement](spec.md#requirement-cancelled-sqlite-writes-release-traceback-retained-cursors) addresses a different failure from a merely slow session close. For example, cancellation during INSERT RETURNING can leave the native cursor in a retained exception frame. Closing the native connection alone can then leave the writer slot held until garbage collection.

File-backed request and background engines now use a connection factory that weakly tracks the cursors SQLAlchemy creates. Cursor creation and cleanup remain on the existing aiosqlite worker. Cleanup attempts every live cursor, then the native connection, even if one cursor raises; the first error remains visible. Weak references avoid extending statement lifetime. In-memory engine construction, other backends, rollback and cancellation ownership retain their existing paths.

The terminal batcher in this fork owns a timed-out append until shutdown rather than cancelling at its observation deadline. Regression coverage therefore exercises its real close/drain cancellation, keeps the commit traceback alive, and verifies an independent writer, incomplete-spool settlement, late-append refusal and leader acquisition for rows_v1 and chunks_v2. These local file-SQLite results do not certify native uvloop timing, other backend execution, distributed races or production.
