## Context

See proposal.md for the five selected rows. Shared selection already resolves model routes, but transport callers omit headers. Retained bridge sessions bypass that selection. Child sticky rows already have a 300-second cap, while socket retention ignores it.

## Goals / Non-Goals

Enforce the existing routing contract before dispatch and retain account ownership. Keep the existing probe and revoked-token algorithms unless regression tests expose defects. No new settings, schema, dashboard UI or live-provider claims.

## Decisions

- Pass incoming routing headers to shared selection. Resolve strict bridge targets before registry locks so reuse observes the same pin. Reject a conflicting required owner instead of replacing it.
- Carry an explicit child idle cap in affinity metadata. This distinguishes a child cap from ordinary short affinity TTL and works for hard turn-state affinity too. Cap retained idle lifetime, never interrupt an active turn.
- A fresh child preference remains advisory, one alternate attempt followed by fallback inside the same deadline. Explicit model routes and required ownership take precedence.
- The preference applies to Codex thread affinity. Generic `/v1/responses` keeps its deliberate non-Codex affinity mode. Fresh lineage proof is stronger than the bridge's follow-up classification based on a thread header.

## Risks / Trade-offs

- Additional route lookup for configured bridge requests: resolve outside locks; unmapped requests do no repository lookup.
- Fake selectors may omit new optional header input: preserve the existing signature compatibility seam.
- Local SQLite and fake upstream evidence cannot confirm real provider/Desktop or distributed/cloud behavior.
