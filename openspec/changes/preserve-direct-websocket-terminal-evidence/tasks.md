## 1. Implementation

- [x] 1.1 In `app/modules/proxy/_service/websocket/mixin.py`, update `_handle_terminal_upstream_websocket_receive` to treat frame-less drops (`_is_account_neutral_transport_drop(message.close_code)`) as account-neutral.
- [x] 1.2 In `app/modules/proxy/_service/websocket/mixin.py`, update `_relay_upstream_websocket_events` to preserve authentic terminal events from continuity owners rather than rewriting to `_rewrite_websocket_previous_response_owner_unavailable_event`.

## 2. Regression Coverage

- [x] 2.1 Add unit test verifying that an abrupt frame-less drop on direct WebSocket does not penalize the account (`penalize_account=False`).
- [x] 2.2 Add unit test verifying that a retryable terminal error from a continuity owner is surfaced to the client with its original error code and message when account migration is unsafe.

## 3. Validation

- [x] 3.1 Run unit tests in `tests/unit/test_proxy_utils.py` and `tests/integration/test_proxy_websocket_responses.py`.
- [x] 3.2 Run migration topology checks.
