## Context

The ring task runs registration and periodic heartbeat through SQLAlchemy sessions. Immediate cancellation can interrupt NullPool's asynchronous SQLite connection close. Existing periodic schedulers already use stop_task_after_grace, which requests cooperative completion and tracks a bounded cancellation fallback for the final clean-shutdown proof.

## Goals / Non-Goals

Finish active ring DB work before stale marking and engine disposal; interrupt idle/retry sleeps immediately. Preserve process deadlines and the incomplete-drain guard. Do not change leader election, membership identity, settings or DB session semantics.

## Decisions

- Add one lifespan-owned stop event shared by ring retry and heartbeat loops. An event-aware bounded wait replaces sleeps so idle tasks stop promptly.
- Use the existing bounded background stop helper after setting the event. Current DB work can finish; a wedged task still reaches cancellation/tracking under the existing grace and process budget.
- Validate the real server with a barrier that holds a ring insert until shutdown commits, then releases it within grace. Preserve no-pool-error, row staleness and exit-bound assertions. Retain existing smoke and poller tests.

## Risks / Trade-offs

- Cooperative completion can briefly finish the current registration during drain -> stale marking follows the stopped task, and admission remains closed.
- Wedged DB work must not pin shutdown -> reuse bounded cancellation and existing undrained-task/clean-marker gates.
- Windows does not implement POSIX SIGTERM semantics -> run Linux isolated-source integration tests and cloud CI as well as portable unit/static checks.
