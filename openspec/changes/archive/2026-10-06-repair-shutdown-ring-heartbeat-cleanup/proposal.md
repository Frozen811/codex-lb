## Why

Exact-head CI exposed SQLite pool reset/close errors during startup SIGTERM. A constrained Linux reproduction identified the ring registration/heartbeat coroutine: lifespan cancelled it immediately while its database connection was closing.

## What Changes

- Stop ring registration/retry/heartbeat cooperatively and finish current DB work within the existing shutdown grace before marking membership stale or disposing engines.
- Make periodic/retry waits wake on stop, retaining bounded cancellation fallback and incomplete-drain tracking.
- Add a real-process SIGTERM barrier regression for an in-flight ring registration transaction.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `graceful-shutdown`: ring membership database work uses the owned, bounded background-task shutdown contract.

## Impact

app/main.py, POSIX shutdown integration regressions, focused lifespan/background-stop tests and OpenSpec/context. No settings, dependencies, migrations, routing-policy changes or weakened assertions.
