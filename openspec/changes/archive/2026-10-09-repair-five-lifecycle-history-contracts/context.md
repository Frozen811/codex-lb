## Scope and rationale

Exactly five source records: UP-PR-2506, UP-PR-2255, UP-PR-2344, UP-PR-2133 and UP-PR-2484. Source author measurements are not reused as local evidence. Existing shutdown, bridge-ring and query-caching contracts remain the source of truth.

## Constraints and failure modes

No new configuration or database schema. Callback transfer can leave a completed settlement registered before its reservation-release fallback is scheduled. Filtering done tasks at that point produces a false zero. Missing or malformed status observations cannot prove drain completion. A slow maintenance call must not block heartbeat or duplicate its own pass. SQLite lock isolation remains limited to connection admission.

## Example

A completed HTTP response has no in-flight handler, but its settlement owner remains registered. Internal drain status reports `request_persistence_state=pending` and `request_persistence_pending=1`, including the callback-transfer window. After all owner callbacks release their tasks it reports `drained` and `0`. If observation cannot be obtained it reports `unknown` and omits the count.

## Verification boundaries

Focused tests and static checks apply to this checkout. Live provider traffic, POSIX SIGTERM, external database engines, cloud CI, public artifacts and production need separate evidence. Previous dirty files and unrelated registry records are preserved.
