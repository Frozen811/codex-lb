## Context

See proposal.md. Registry sources were read from live GitHub on 2026-10-09. The checkout contains a prior five-item package, backed up with SHA256 hashes outside the repository before edits.

## Goals / Non-Goals

Preserve task ownership through completion callbacks and stop interruption. Remove optional work from the heartbeat critical path. Keep existing WebSocket denial and history-cap contracts independently protected. No DB migrations or UI work; no publication or production certification.

## Decisions

- Observe registered persistence owners, including done tasks whose callbacks have not released ownership. Derive pending/drained from a validated nonnegative integer count; report unknown without a count when observation is absent, invalid or throwing. Preserve existing activity fields.
- Track a cancellation-deferring background task as soon as fallback cancellation begins. An interrupted stop caller cannot erase its ownership; cooperative grace interruption still propagates without cancelling the worker.
- Give durable reconciliation, stale-operation cleanup, idle sweeping and cap refresh separate periodic owners after registration. Each owner awaits its current pass before another tick, catches ordinary failures and wakes on the shared stop event. Heartbeat uses the background DB provider; explicit session factories remain supported for tests and other consumers.
- Stop all maintenance owners before stale marking and DB disposal, using the existing bounded helper and incomplete-task clean-shutdown gate.
- Verify the existing capped SQLite query at cutoff/floor boundaries and timestamp ties rather than introducing a new query or cache layer.
- Preserve the fork's current readiness response contract; the upstream PR's ancillary readiness envelope redesign is not transplanted as part of the registry record's heartbeat-isolation concern. Health/readiness and stable ring fingerprint controls are rerun independently.

## Risks / Trade-offs

- SQLite still has one writer lock: background-pool separation isolates connection admission, not file-lock contention.
- A wedged optional phase remains single-flight; bounded shutdown cancellation tracks it if it cannot finish.
- A drained observation proves absence of current ownership, not past write success or an atomic stop certificate.
- POSIX process tests cannot run on this Windows host; deterministic asynchronous lifecycle and file-backed SQLite checks provide bounded local evidence.
