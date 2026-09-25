# Proposal: Dashboard Model Source Visibility, Upstream Transport Parity, Compaction Switchover, and Safe Slimming

## Why

1. **Issue #1870**: When request logs belong to configured upstream model sources (`modelSourceId`) rather than local ChatGPT/API accounts, the dashboard formerly displayed `Unassigned` in the Account column, making it impossible to identify which provider served the request or distinguish between sources serving the same model slug. Additionally, the request details dialog omitted the model source ID and kind.
2. **Issue #1208**: Requests originating from or passing through proxies can have identifying fingerprints (TLS implementations, HTTP/2 frame and window parameters, casing of headers, non-native SDK headers like `x-stainless-*` and `x-openai-client-*`). Upstream parity requires matching official Codex CLI fingerprints (Rustls TLS, exact H2 stream/connection windows, header position and casing restoration, and normalizing non-native requests).
3. **Issue #986**: Mid-conversation switchover across sticky accounts breaks upstream prompt-cache locality and causes expensive re-billing of input tokens. Reallocating sticky accounts should be deferred until a compaction boundary or explicit re-anchoring when context is already reset.
4. **Issue #568**: Naive conversation history truncation and inserting fake assistant messages (`[codex-lb omitted N items]`) corrupted conversation context, caused prompt-cache misses, model hallucinations, and WebSocket `turn_state` mismatches. Slimming must strictly target historical large tool outputs and historical large images while leaving conversation sequences intact.

## What Changes

- **Dashboard Model Source Visibility**:
  - Update `recent-requests-table.tsx` so that `accountLabel` falls back to `request.modelSourceId` when `request.accountId` is null.
  - Expose `modelSourceId` and `modelSourceKind` in the request details modal under the metadata grid.
  - Provide complete localization across `en.json`, `ko.json`, and `zh-CN.json`.
  - Add unit test coverage in `recent-requests-table.test.tsx`.
- **Upstream Transport Parity & Fingerprint Normalization**:
  - Ensure native egress (`codex-lb-native-egress`) uses Rustls TLS, configured HTTP/2 window sizes (2MB stream / 5MB connection), and standard frame limits matching Codex CLI.
  - Normalize non-native SDK headers, stripping `x-stainless-*` and `x-openai-client-*` families and setting canonical `codex_cli_rs` User-Agent and originator.
- **Sticky Compaction Switchover**:
  - Maintain `reallocate_sticky=False` for normal turns, deferring sticky account reallocation to compaction boundaries (`compact.py`) where `reallocate_sticky=True` is explicitly activated.
- **Safe Payload Slimming**:
  - Restrict inline proxy slimming to historical tool outputs and large inline images, preserving conversation message continuity and prompt cache.

## Capabilities

### Modified Capabilities
- `frontend-architecture`: The recent-requests table renders `modelSourceId` when `accountId` is absent, and the request details dialog exposes `modelSourceId` and `modelSourceKind`.
- `outbound-http-clients`: Upstream HTTP/2 requests match the official Codex client profile, and non-native SDK fingerprints are normalized.
- `sticky-session-operations`: Sticky thread reallocation is deferred during ongoing conversations and permitted across compaction boundaries.
