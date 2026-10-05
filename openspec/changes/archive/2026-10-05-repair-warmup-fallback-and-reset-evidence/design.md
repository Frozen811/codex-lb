## Context

See proposal.md. The fallback consumes a Responses SSE iterator. An EOF currently reaches a synthetic completed compact result even without response.completed. Idle-slot timing already computes a stable epoch cycle for sliding deadlines, but the persisted claim uses the moving upstream deadline.

## Goals / Non-Goals

Preserve selected-account ownership, existing authentication, opt-in policy, cooldowns, and compact fallback on 404 only. Provider availability and production deployments are outside the local verification scope.

## Decisions

- Require response.completed before returning fallback success. An absent terminal produces stream_incomplete; do not manufacture usage when upstream omits it. Keep one fallback and existing finally cleanup.
- Omit max_output_tokens at the fallback producer, consistent with operator probes and the existing transport field filter.
- Use the computed cycle end as the primary_idle claim deadline. For ordinary fixed cycles this equals the upstream deadline. Non-zero slots retain existing sliding-horizon detection. Slot zero uses the epoch phase only after consecutive usage observations prove a matching advance in reset deadline and observation clock; this preserves the initial phase of fixed windows.
- Verify live ingestion with the real scheduler and SQLite repositories, keeping existing reset-history recovery unless a failure proves a further change necessary.

## Risks / Trade-offs

Old moving-deadline idle claims may differ from the first stable-cycle claim after upgrade; existing cooldown limits the transition. Stable cycles can intentionally defer a late evaluation to the next slot. Keep current grace and observed-duration rules. Cancellation/fan-out architecture is not changed.
