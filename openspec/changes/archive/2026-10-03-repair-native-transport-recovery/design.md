## Context

See proposal.md. Direct streams already pass account IDs through the IPC protocol to Rust ClientKey and explicitly close nested generators. Independent tests must exercise those boundaries rather than repeat key serialization or simulated lease counters.

## Goals / Non-Goals

Goals: typed Windows route parity, generation-safe rotation, no ambiguous replay, actual HTTP/2 partitioning and real admission/settlement after native EOF/failure.

Non-goals: raw upstream error-chain disclosure, macOS TCP offload diagnosis, live provider certification, release or production changes. The wider #2471 diagnostics/WebSocket asks remain separately tracked.

## Decisions

- Replace 64/121 with 1231/1232 in the Windows-specific process-network set. Reset and timeout remain account/endpoint attributed, matching existing POSIX semantics. Message text never establishes provenance.
- Keep the existing connector-only pre-dispatch decision and generation compare-and-swap rotation. A missing response head does not prove a POST was never executed.
- Exercise the compiled helper against a local TLS HTTP/2 origin with a temporary trusted CA. Observe physical connections and terminate one while another account's stream is live. Reuse the existing h2 test dependency and helper test-binary opt-in.
- Exercise actual Responses routes, database reservations and account concurrency state. Require a later request to succeed at stream limit one after repeated failures.
- Pass an attempt-owned typed failure trace through the core stream call. Capture native phase, static exception category and observed status before yielding a synthetic terminal, then consume it at the request-log boundary only when stronger failure metadata is absent. This keeps diagnostics out of event payloads and preserves existing cancellation/error classification.

## Risks / Trade-offs

- Native tests need a source-built helper and h2; verification explicitly supplies both. Missing prerequisites must be reported as skips, never passes.
- Windows errors are injected as typed errors at the HTTP session boundary; this proves application handling rather than real adapter loss.
- Controlled HTTP/2/EOF cannot certify macOS offload behavior or public packages.

## Migration Plan

No schema or configuration migration. The local source correction is reversible; deployment and publication require their own evidence.
