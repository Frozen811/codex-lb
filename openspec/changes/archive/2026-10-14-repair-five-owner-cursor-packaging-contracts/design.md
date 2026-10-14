## Context

See proposal.md for the exact five-row scope. SQLite's native close can leave a RETURNING statement alive through a cancellation traceback. SQLAlchemy creates cursors on aiosqlite's existing worker. The WebSocket decision already knows whether the preferred account is required, but passes that constraint only for model rejection.

## Goals / Non-Goals

**Goals:** Preserve error identity, release cancelled writers and document native normalization accurately.

**Non-Goals:** No new retries, schema, settings, provider support, deployment or dependency upgrades beyond the already-present urllib3 floor.

## Decisions

- Use the existing hard-owner constraint for every connect failure decision, including exhausted 401 refresh attempts. Soft preferences retain failover. Keep existing classification, stream lease release and deferred API-key settlement.
- Use a sqlite3.Connection subclass with weak cursor tracking; finalize cursors before native close on the existing aiosqlite worker. Do not rely on garbage collection or change SQLAlchemy versions. Attempt remaining closes after errors and propagate the first error after native connection close.
- Install the factory through shared file-backed engine kwargs, covering request and background paths. Keep in-memory engine configuration unchanged.
- Move the normalizer docstring before statements and clarify shared reasoning/error/terminal normalization and native quota projection. Compare executable AST after removing documentation to prove no wire logic changed.
- Independently verify the existing Docker OAuth override with rendered Compose config and existing tests, and inspect a locally built wheel's urllib3 dependency metadata. Live Docker startup and image scanning remain separate evidence.

## Risks / Trade-offs

- Retained cursors are uncommon but can strand all writers: reproduce with real file SQLite and retained cancellation frames, plus both terminal spool formats.
- Owner constraints must not strand movable requests: cover both hard-owner refusals and ordinary failover.
- A doc-only patch can inadvertently affect the generator: compare normalized AST and run stream lifecycle regressions.
- Local tests do not establish provider, hosted CI or production results: state those limits in verification and saved registry rows.
