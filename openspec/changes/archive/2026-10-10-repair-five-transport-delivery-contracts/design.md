## Context

See proposal.md. The current bridge has per-queue event/byte caps and a five-second enqueue timeout. Queue detachment already uses non-cancelling shutdown. The 251 dirty files are snapshotted outside the repository.

## Goals / Non-Goals

Bound all retained live queue payload, including blocked enqueue calls. Keep accepted output in order, fail only the affected request, release reservations, and allow sibling turns to continue. Completed replay/spool storage, total interpreter memory, production performance and upstream policy acceptance are separate scopes.

## Decisions

- Use one fixed process budget of 256 MiB with synchronous reserve/release operations. Reserve before waiting for per-queue capacity, so blocked producers count. Reject excess immediately instead of retaining an unaccounted waiter payload.
- Each queue owns a byte account; finalization releases abandoned accounts without retaining the queue. Pending reservations release idempotently on cancellation, finish, fail or detach. Dequeue and immediate shutdown release queued bytes.
- Keep current per-queue limits and five-second delivery stall bound. A small bounded failure envelope is terminal metadata, outside the live-output payload budget. Budget failure uses the existing downstream backpressure path and ordered prefix/failure/EOS delivery.
- Verify the four existing behaviors using current helper and route tests, adding boundary coverage where necessary. Typed provenance remains authoritative; genuine upstream capacity recovery remains available.

## Risks / Trade-offs

- Many paused queues can make a healthy producer encounter the process budget: fail only that downstream operation, retain its accepted prefix and preserve upstream sibling work.
- Double release after detach/cancellation: reservations are idempotent and queue accounting is owned until dequeue or finalization.
- Payload accounting is UTF-8 output size, not Python heap/RSS, spool or completed replay size. Test small injected budgets deterministically; keep those boundaries explicit in context/evidence.
