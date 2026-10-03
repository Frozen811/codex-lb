## Context

See proposal.md for the three audit IDs. Clock update validation already uses an ASCII range pattern, but the response applies a format constraint to historical strings. The SCIM reader streams a bounded bytearray but its declared-length precheck calls int() after isdigit(). Cache publication already restores pending markers in finally.

## Goals / Non-Goals

Goals: retain strict admission and make existing failure contracts executable at external routes. Keep real database writes and peer cache refreshes in the invalidation verification.

Non-goals: new planner settings, transport header parsing policy outside SCIM, distributed durable outbox delivery across source-process loss, public release, or production infrastructure changes.

## Decisions

- Validate newly supplied times strictly; return historical strings verbatim. Normalizing legacy data on read would hide what the operator needs to repair and change existing data implicitly.
- Check ASCII decimal syntax and compare a zero-stripped length against the short decimal route budget. This avoids arbitrary integer conversion limits and preserves leading-zero semantics without unbounded numeric conversion.
- Verify POST/PUT/PATCH stream crossings, exact-size valid bodies, malformed lengths, and unchanged database state with real SCIM token admission. Retain global ingress middleware.
- Verify direct publication failure after an operator Pause, then retry via the owning poller and refresh a separate database-backed routing cache. Existing cache code changes only if tests reveal a defect; the pending-marker implementation already covers cancellation.

## Risks / Trade-offs

- In-memory pending markers disappear with source-process loss: preserve the documented TTL/reconcile backstop and do not claim durable queue delivery.
- A real HTTP server can reject malformed framing before ASGI: test the SCIM route's behavior when such a header reaches it, without making guarantees for h11 or nginx.
- Read schemas accept malformed historical values: request schemas remain strict, and regression tests assert atomic invalid-update refusal.

## Migration Plan

No database migration. Apply code and tests together; preserve previous local work. Rollback is limited to this batch's patches.
