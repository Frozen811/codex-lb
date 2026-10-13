## Context

See proposal.md. The checkout includes 489 dirty files and 338 source registry rows. Current HTTP timing, drain observation and scheduler grace already implement their contracts. Admission and quota patches are adapted from community PRs [2561](https://github.com/Soju06/codex-lb/pull/2561) and [2308](https://github.com/Soju06/codex-lb/pull/2308), with their existing attribution retained in this change.

## Goals / Non-Goals

Goals: effective dashboard cap admission and pooled, privacy-respecting telemetry across native transports. Non-goals: upstream deployment, performance certification, identity or quota policy replacement and unrelated dirty fixes.

## Decisions

- Use a frozen snapshot of effective caps, tunables and fair-share threshold from one settings row before pending_lock. Retain current fresh-owner checks at both admission boundaries and the held-lease fast path.
- Rebuild quota events from downstream header parsing; never merge raw account fields. SSE uses its request header snapshot; WebSocket resolves the existing quota cache after raw ingestion. Preserve cancellation and omit metadata on cache failure.
- Reuse the existing SSE block parser to cover source chunk boundaries and existing response cleanup owners. Keep public OpenAI event filtering unchanged.
- Use existing regressions for the three implemented contracts, supplementing ownership/real database behavior where needed. Do not edit production code solely to manufacture fixes.

## Risks / Trade-offs

Settings can stall before admission: cancellation must unregister the waiter and leave pending_lock available. Quota cache errors must not fail inference. Windows cannot exercise POSIX SIGTERM tests directly: retain platform skips and seek an available isolated Linux runtime. Local proof does not imply native client/provider or hosted CI acceptance.

## Migration Plan

No database or configuration migration. Publication and deployment require separate authorization. Synchronize stable specs/context and archive only after focused verification.
