## 1. Implementation

- [x] 1.1 Update `_is_account_neutral_transport_drop` in `app/modules/proxy/_service/streaming/helpers.py` so that `close_code in (None, 1006)` is account-neutral regardless of `response_events_seen`.
- [x] 1.2 In `app/modules/proxy/_service/http_bridge/upstream_events.py`, ensure `account_neutral_transport_drop` does not require `not upstream_output_observed`.
- [x] 1.3 Ensure `_record_http_bridge_account_timeout_signal` is only recorded for eventless drops (`observed_response_events == 0 and not upstream_output_observed`).

## 2. Regression Coverage

- [x] 2.1 Update `test_account_neutral_transport_drop_requires_no_close_frame_and_no_response_events` in `tests/unit/test_proxy_utils.py` to assert that frame-less drops with `response_events_seen > 0` are account-neutral.
- [x] 2.2 Update `test_http_bridge_drop_after_streamed_events_still_penalizes_account` in `tests/unit/test_proxy_http_bridge.py` so that a frame-less drop after streamed events sets `penalize_account is False` and does not record an eventless drop signal.
- [x] 2.3 Add test asserting that non-clean close frames (e.g. 1008, 1011) after streamed events still penalize the account.

## 3. Validation

- [x] 3.1 Run unit tests in `tests/unit/test_proxy_http_bridge.py` and `tests/unit/test_proxy_utils.py`.
- [x] 3.2 Run migration topology checks.
- [x] 3.3 Validate OpenSpec specs: `uv run openspec validate --specs`.
