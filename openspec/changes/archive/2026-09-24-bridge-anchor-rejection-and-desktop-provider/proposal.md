# Proposal: Bridge Anchor Rejection Stream Terminal, Desktop OpenAI Provider, and Telemetry Opt-Out Hardening

## Why

1. **Issue #2493**: When an HTTP Responses request to the HTTP-to-WebSocket bridge fails due to a rejected proxy-injected anchor (`previous_response_not_found`), if keepalive bytes were previously yielded downstream or if the startup probe encountered `bridge_previous_response_not_found`, the stream was abruptly disconnected or returned a raw JSON error response instead of a native SSE terminal event (`response.failed` with retryable code). This caused native Codex clients to abort with `stream disconnected before completion: stream closed before response.completed`.
2. **Issue #2262**: Codex Desktop configurations routing through codex-lb typically used a custom provider name (e.g., `model_provider = "codex-lb"`), which broke synchronization between web/mobile chat conversations and Desktop. Allowing operators and users to directly override the built-in `[model_providers.openai]` with codex-lb's `/backend-api/codex` endpoint preserves provider identity and seamless session sync.
3. **Issue #1844**: In the anonymous telemetry subsystem, a TOCTOU race existed between consent re-checking and snapshot transmission, where disabling telemetry concurrently could still transmit a snapshot in-flight. Furthermore, `TelemetryOptOut.occurred_at` lacked datetime typing flexibility, and requesting previews under the env kill switch (`CODEX_LB_TELEMETRY_ENABLED=false`) could trigger database writes to mint an instance identity.

## What Changes

- **Responses Stream Lifecycle & Error Handling**:
  - Update `yield keepalive_event` in `streaming.py` to record `yielded_any = True` so subsequent terminal events are yielded as SSE rather than attempting to raise an exception over a committed HTTP 200 stream.
  - Include `"bridge_previous_response_not_found"` in `SYNTHETIC_TRANSPORT_FAILURE_CODES` in `app/core/errors.py`.
  - Include `"bridge_previous_response_not_found"` in `native_transport_startup_failure` and `_stream_response_error_events` in `app/modules/proxy/api.py`.
  - Ensure `_is_previous_response_not_found_public_error` recognizes `bridge_previous_response_not_found` and masks it into standard `stream_incomplete` 502 with `PREVIOUS_RESPONSE_STREAM_INCOMPLETE_MESSAGE`.
- **Codex Desktop Configuration & Documentation**:
  - Document the built-in `[model_providers.openai]` configuration override in `docs/client-setup.md` and `docs/examples/codex/config.toml`.
  - Add regression coverage in `tests/unit/test_codex_upstream_paths.py` verifying `/backend-api/codex` handles requests from this configuration.
- **Telemetry Opt-Out Hardening**:
  - Close the TOCTOU race between consent re-check and snapshot transmission using a shared `asyncio.Lock` in `TelemetrySender`.
  - Support `datetime | str` in `TelemetryOptOut.occurred_at` in `app/modules/telemetry/schemas.py`.
  - Suppress identity generation and DB writes for preview generation in `app/modules/telemetry/api.py` when telemetry is disabled via environment variable (`CODEX_LB_TELEMETRY_ENABLED=false`).

## Capabilities

### Modified Capabilities
- `responses-api-compat`: Native streaming clients receive a valid SSE `response.failed` event on proxy-injected anchor rejection even after keepalive events or during probe startup.
- `user-documentation`: Document the option to preserve the built-in OpenAI provider identity in Codex Desktop.
- `telemetry`: Synchronize snapshot transmission and opt-out, accept `datetime` in opt-out payloads, and prevent identity DB writes under the environment kill switch.
