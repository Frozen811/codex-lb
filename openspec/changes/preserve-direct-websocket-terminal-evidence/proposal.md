# Why

Direct `/v1/responses` and `/backend-api/codex/responses` WebSocket traffic has
two related terminal-evidence classification gaps (Issue #2081):
1. A terminal upstream WebSocket ending with no upstream-authored close frame
   (`None` or adapter-synthesized RFC 6455 `1006`) is charged to the serving
   account on the direct path, even though the HTTP bridge now treats the same
   structured transport evidence as account-neutral.
2. When an already-selected continuity owner returns a retryable terminal event
   and account migration is unsafe, the direct path replaces that real event
   with `Previous response owner account is unavailable`, even though owner
   selection already succeeded and the terminal is genuine application evidence
   (e.g. rate limit or server error from the owner). The client loses the actual
   upstream error message, retry-after hints, and error classification.

# What Changes

- In `_handle_terminal_upstream_websocket_receive` (direct WebSocket reader),
  classify frame-less upstream endings (`_is_account_neutral_transport_drop(message.close_code)`)
  as account-neutral (`penalize_account=False`).
- In `_relay_upstream_websocket_events` (direct WebSocket event relay), when a
  continuity owner returns a retryable terminal event and account migration is
  unsafe or impossible, preserve the authentic terminal event (error code,
  message, retry-after) instead of rewriting it to
  `_rewrite_websocket_previous_response_owner_unavailable_event`.
- The account's rate-limit or error status is still recorded via
  `_handle_stream_error`, but the client receives the honest upstream event.

# Capabilities

## Modified Capabilities

- `responses-api-compat`: Direct WebSocket connections preserve account-neutrality
  for frame-less transport drops and surface authentic terminal error events
  from continuity owners.

# Impact

Direct WebSocket clients receive accurate upstream error details and retry hints
instead of synthetic 502 owner-unavailable errors, and accounts are not penalized
for frame-less transport drops on direct WebSocket streams.
