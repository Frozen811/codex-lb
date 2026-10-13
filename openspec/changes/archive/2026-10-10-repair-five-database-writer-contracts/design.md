## Context

See proposal.md. Existing file-backed SQLite writers share an anyio lock, but an integer ContextVar treats child tasks as nested owners. OAuth flow persistence, auth limit writes, fingerprint verification and lease operations bypass admission. Session reclaim registers completion callbacks only after its awaited interrupt.

## Goals / Non-Goals

Preserve same-task nesting, database-clock lease deadlines, monotonic OAuth success, login limiting and fingerprint mismatch refusal. Establish local task/transaction ownership without adding settings or modifying migration history. Production incident reproduction and distributed throughput tuning remain external.

## Decisions

- Compare the reentrancy context with the current asyncio task. A copied context does not confer ownership. Parent tasks must leave their section before awaiting children that need it.
- Admit auth-limit writes with the existing gate and keep OAuth/fingerprint/lease session cleanup inside admission. Only database work holds the gate; password verification and OAuth network exchange stay outside.
- Defer cancellation during driver interrupt, finish connection invalidation and register late-close callbacks before propagating it. Keep failure logs and existing bounds; interruption is best effort, not proof of release.
- Reuse existing owner-before-key locking and product race tests on an isolated PostgreSQL container. A SQLite pass cannot prove that race.

## Risks / Trade-offs

Changing task ownership exposes callers that awaited child writes while holding admission; focused affected suites and source inspection cover this. Serialization can delay a lease beyond expiry; existing execution-time database predicates must continue refusing resurrection. Unrecoverable native worker failure retains bounded cleanup and diagnostics.
