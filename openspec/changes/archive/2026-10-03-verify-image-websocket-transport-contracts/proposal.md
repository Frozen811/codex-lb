# Proposal

## Why

UP-ISSUE-2425, UP-ISSUE-2081 and UP-ISSUE-1208 are marked resolved by source claims but lack independent local registry evidence. Direct error-kind WebSocket endings lack explicit terminal provenance, and native JSON request compression is absent.

## What Changes

- Verify bounded inline-image bridge reuse and failure recovery at the public and backend routes.
- Carry typed transport-ending evidence from WebSocket adapters so actual frame-less endings remain account-neutral without making protocol-invalid frames neutral.
- Verify selected-owner terminal preservation, settlement and replay refusal.
- Add controlled zstd encoding for native Codex Responses JSON requests and verify headers, decoded body and HTTP/2 on a loopback TLS origin.
- Document the native and Python transport boundaries without promising an indistinguishable client fingerprint.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: positive direct WebSocket ending provenance and owner terminal preservation.
- `outbound-http-clients`: scoped native Responses request compression and explicit transport guarantees.

## Impact

WebSocket adapters, direct relay classification, native HTTP request preparation, focused integration tests and the three registry rows. No settings, schema migration, publication or deployment.
