## Context

See proposal.md. Existing recovery registration uses reversible durable receipts and local/durable alias ownership fences. Native stream delivery distinguishes a local refusal from a transport ending using explicit exception provenance. Error codes alone cannot establish dispatch ownership.

## Goals / Non-Goals

Verify the three selected product contracts with real SQLite persistence and route execution. Preserve live parent lanes, explicit anchors, file ownership, reservation settlement and cancellation. Hosted clients, production traffic and cloud gates are outside the local batch.

## Decisions

- Keep guarded recovery alias registration. A model-transition child retains the downstream continuity token for registration while clearing the parent identity from upstream submission. Verify turn N+1 and refuse alias theft from a protected live parent.
- Mark each statically pre-dispatch refusal individually. Keep local refusal provenance separate from permission to replay over raw HTTP; an anchored refusal must be delivered without gaining replay authority.
- Preserve the existing post-terminal health helper. Test its first-event, later-event and exception paths through public routes with actual reservation settlement, rather than adding another finalizer.

## Risks / Trade-offs

- A blanket transport-code sweep could hide a real upstream ending. Record a per-site verdict, retaining transport/reconnect and already-dispatched paths.
- Recovery aliases can conflict with a still-live parent. Existing protected-alias and rollback controls must continue to fail closed.
- Mocked dispatch state is not live-provider evidence. Loopback upstreams and real database readback establish only the bounded local contract.
