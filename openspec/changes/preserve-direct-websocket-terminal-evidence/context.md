# Context: Direct WebSocket Terminal Evidence Parity

## Background & Rationale

Direct WebSocket clients communicating with `/v1/responses` or `/backend-api/codex/responses`
can encounter two issues regarding terminal evidence:

1. Transport Drop Parity:
   When an upstream WebSocket drops without an RFC 6455 close frame (e.g. abrupt disconnect,
   code 1006 or None), the HTTP bridge treats this transport drop as account-neutral.
   However, the direct WebSocket reader (`_handle_terminal_upstream_websocket_receive`)
   only checked `is_account_neutral_websocket_error_code`, which did not check
   `_is_account_neutral_transport_drop(message.close_code)`. As a result, direct
   WebSocket traffic penalized the account with `record_error` for network drops.

2. Authentic Continuity Owner Terminal Errors:
   When an anchored turn routes to its continuity owner, and that owner emits a terminal
   event such as `rate_limit_exceeded` (429) or `server_error` (500), if the turn cannot
   be safely migrated to another account (e.g. because of session/turn state pinning),
   the direct relay was rewriting the terminal event into:
   `upstream_unavailable / "Previous response owner account is unavailable; retry later."`
   This hid the genuine upstream failure from the client, stripped `retry_after` hints,
   and confused users and client SDKs into thinking the account was missing or disconnected
   rather than rate-limited.

## Decisions

- In `_handle_terminal_upstream_websocket_receive`, define `account_neutral_drop = _is_account_neutral_transport_drop(message.close_code)`.
  When `account_neutral_drop` is True, `penalize_account=False`.
- In `_relay_upstream_websocket_events`, when an owner returns a terminal error code in
  `_WEBSOCKET_TRANSPARENT_REPLAY_ERROR_CODES` and `not retry_safe_owner_replay`:
  Call `_handle_stream_error` to mark the account's state, clear `retry_error_code = None`,
  and do NOT rewrite the event to `_rewrite_websocket_previous_response_owner_unavailable_event`.
  Forward the authentic upstream event to downstream.
