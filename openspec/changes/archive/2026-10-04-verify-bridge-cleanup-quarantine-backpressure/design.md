## Context

See proposal.md. The current repository already implements queue byte/event limits, quarantine owner references and worker-wide monotonic generations. Scheduled purge selects a timestamp/generation snapshot but omits the failure count and loops over the same stale candidates after partial success.

## Goals / Non-Goals

Goals: preserve concurrent retry writes, release detached output promptly, and prove the selected claims at the scheduled cleanup and HTTP bridge boundaries. No migration or new setting is required.

Non-goals: process-crash claim reclamation (UP-ISSUE-2271), native-helper/process-wide memory budgets, vendor traffic and public release validation.

## Decisions

- Keyset pagination over the existing composite primary key visits every selected key at most once. A failed CAS is preserved for the next scheduled pass; an in-memory exclusion set would grow with the whole purge and SQL exclusions would grow with each batch.
- The selected failure count joins timestamp/generation in the delete fence. Existing age and continuity predicates still apply at deletion time.
- Closing a detached queue discards its payloads and removes/cancels waiters; cancellation cleanup follows asyncio queue semantics. Delivery failure must be observable to a resumed consumer and must not escape as cancellation of the shared reader.
- Verify quarantine through completion/settlement interleavings before changing existing policy. Distinguish local fencing evidence from supported database and overflow-policy scope.

## Risks / Trade-offs

- Concurrent insertion behind a purge cursor waits for the next pass, which preserves new protection.
- Per-stream queue limits do not certify a process-wide RSS ceiling or native helper queues. The existing lone oversized event exception remains a documented bounded-frame limitation unless regression evidence requires changing it.
- An output delivery failure can occur after upstream completion. Client-visible delivery and upstream settlement must remain separate; reservations must finish once without an account penalty.
