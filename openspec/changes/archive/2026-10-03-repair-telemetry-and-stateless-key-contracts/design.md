## Context

See proposal.md for the three registry items. The sender holds a process lock only around final snapshot POST, while registration/activation and dashboard commits can race. Environment-key encryption already exists and needs proof and contract synchronization.

## Goals / Non-Goals

Goals: order the complete local protocol, validate timestamp shape, and prove persisted client aggregation and key selection. Non-goals: collector changes, cross-process fences, new settings, key rotation, public releases, or PostgreSQL deployment certification.

## Decisions

Reuse the sender process lock and expose its accessor to the telemetry API. Place the fresh consent/identity read before registration and hold ownership through activation and final POST. Serialize the API's previous-state read, decision commit, and opt-out scheduling using that same lock. The existing five-second send timeout bounds network waits; cancellation unwinds the async context. This avoids a generation/wire-schema change. Other processes still require collector authority.

Use a typed datetime for occurred_at and the existing UTC serialization convention. Valid strings stay accepted through model parsing while invalid strings fail. Verify environment keys with actual Settings, persisted account import/readback, separate encryptors and database sentinel checks rather than changing working crypto.

Use only loopback collector servers with controlled events in tests; await or cancel every task and reset test lock state per loop. Persist actual request logs and inspect the real preview response for all documented groups.

## Risks / Trade-offs

A dashboard save can wait up to the bounded active send timeout. An in-flight snapshot completes before disable commits; it cannot be recalled from the remote collector. The lock orders one event loop/process only. Remote acknowledgements, cross-process in-flight requests, collector retention, and hosted traffic remain external verification scope.

## Migration Plan

No schema migration or dependency changes. Deploying the source change uses existing procedures; this local repair batch performs no deployment.
