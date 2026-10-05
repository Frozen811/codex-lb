## Context

See proposal.md. The current ImportDialog accepts one File while AccountsPage already supplies a per-file mutation that refreshes accounts and retains errors. Existing backend contracts implement Prolite aliases, canonical client telemetry and complete WebSocket JSON parsing.

## Goals / Non-Goals

Keep one active import and preserve the pending suffix without changing the backend. Verify existing fixes independently. Broader upstream feature stacks, real provider sessions and production deployment are outside this batch.

## Decisions

Keep the existing per-file callback. Own a local submitting flag for the full batch because a mutation's busy state can flicker between files. Use a synchronous submission guard as well as disabled UI controls. Display filenames only; retain File objects in component memory and never persist credentials to browser storage. Stop on the first rejected promise, allowing the existing mutation error to explain failure. Reset the browser file input after failure or completion so reselecting the same file works.

Use the current shared Model Source form and test both consumer dialogs. Use persisted SQLite request logs for telemetry proof and a real loopback WebSocket for bridge framing proof; helper checks alone do not establish those contracts.

## Risks / Trade-offs

Successful imports are retained if a later file fails; the batch is deliberately not atomic. A rejected request can have an uncertain remote outcome, so retry uses the existing import API's identity handling. Parent unmount remains owned by the surrounding app. No new timers, settings or concurrency mechanisms are introduced.
