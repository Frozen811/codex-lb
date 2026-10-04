## Context

The selected source rows are initially НЕ ПРОВЕРЕНО. The base HEAD is 282ce147038ac53b72bca30d69c4ad9a9ac1b7cc; unrelated dirty files are retained. Existing code counts reason-only incomplete terminals and maps elapsed persisted cooldowns to zero.

## Goals / Non-Goals

Verify those contracts and repair cancellation/late cleanup in the existing claim path. Owner process death, uncertain internal DB timeout, claim ABA after generation rollback, cross-database execution and a new abandonment policy are residuals, not claims of full closure.

## Decisions

- Use the existing scheduler and `_await_task_deferring_cancellation` to own the bounded claim task. Store a successful claim on the request before re-raising cancellation, so submission's finalizer releases it without dispatch.
- Durable release does not mutate local half-open state. Submission already releases the exact local lease it owns; duplicating that operation without its lease token corrupts newer state.
- Preserve the current ambiguous-send guard, per-key claim timeout and generation/epoch CAS.
- Validate through loopback WebSocket/HTTP routes, real isolated SQLite and focused existing ownership/settlement tests.

## Risks / Trade-offs

Cancellation may wait for the existing five-second claim timeout. An internal timeout can still leave an uncertain committed claim. A reported Retry-After bound is not proof that a dead worker's claim is reclaimable; retain that external scope explicitly.
