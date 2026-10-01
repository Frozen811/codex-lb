## Context

See proposal.md for the problem. AccountsService.pause_account commits PAUSED, marks local routing unavailable and propagates the existing invalidation namespace. HTTP bridge reuse consults this marker. Direct WebSocket ordinary reuse bypasses connect-time selection; only special conversation/capability paths revalidate. Its create admission can also await after account selection.

## Goals / Non-Goals

**Goals:** close the ordinary direct WebSocket bypass at the final unsent dispatch boundary, preserving existing cleanup and ownership.

**Non-Goals:** cancel work already sent, change routing strategies, infer client quota incidents, add per-turn DB reads or change cross-replica propagation.

## Decisions

- Consult the existing routing availability marker immediately before binding the dispatch owner and send. Rechecking only before admission would leave an await-time race. Re-selecting on every socket turn would add selection/leases and could rebind payload ownership.
- Raise the existing ProxyResponseError with local_pre_dispatch_refusal so the established terminal handler releases the unsent reservation/create admission. Use existing upstream_unavailable / previous_response_owner_unavailable error codes.
- Keep the shared socket/reader alive for already-sent work. Refuse the new frame rather than reconnecting it to a different account or closing other responses.
- Verify real DB account selection and public Pause, stubbing only upstream transport and token refresh. Exercise both ingress routes, anchored/fresh turns and delayed create admission.

## Risks / Trade-offs

- Peer Pause remains subject to the documented invalidation convergence bound. No new distributed locking is introduced.
- A Pause after send begins cannot prove upstream non-delivery; this guard defines a pre-send boundary, not retroactive cancellation.
- Existing mock transports need not fabricate account status: the marker carries canonical mutation/snapshot state.

## Migration Plan

No schema/config migration. Local source change only; publication requires separately authorized commit/push and current-head cloud checks. Roll back the guard without altering stored state if a release regression is found.
