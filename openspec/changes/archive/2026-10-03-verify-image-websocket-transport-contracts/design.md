# Design

## Context

See proposal.md. Bounded inline-image admission and owner terminal preservation already exist. The direct relay only recognizes close-kind frame-less endings, although direct adapters expose incomplete close handshakes as error-kind messages.

## Goals / Non-Goals

Verify all three registry scopes locally and correct observable gaps. No claim of production overload rates, a matching TLS ClientHello, real-client wire identity, or hosted provider acceptance.

## Decisions

- Add a default-false typed transport_ended field. Set it only at adapters with terminal evidence; protocol-invalid errors remain distinguishable. Reuse the shared frame-less close classifier and leave replay safety unchanged.
- Opt in prepared native Responses/compact JSON POSTs to deterministic zstd at the subprocess serialization boundary. Raw relays remain byte-preserving. Existing zstandard dependency supplies level-3 encoding. Python fallback retains its original kwargs and headers.
- Test the public/backend routes and a TLS HTTP/2 loopback origin using the source-built helper. Snapshot controlled headers and decompressed JSON, not volatile version lookup or claimed production fingerprints.

## Risks / Trade-offs

Compression adds CPU work and changes the native upstream representation. Bound it to JSON Responses POSTs and test fallback, compact and opaque boundaries. Production overload recovery cannot be quantified with a local origin; report it as residual evidence.

## Migration Plan

No database or settings migration. Changes remain local; future source deployment must ship the tested adapter code. Rollback is a source revert.
