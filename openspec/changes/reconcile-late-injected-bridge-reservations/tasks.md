## 1. Implementation

- [x] 1.1 In `app/modules/api_keys/repository.py`, add `update_reservation_item_reserved_delta` and `add_usage_reservation_item`.
- [x] 1.2 In `app/modules/api_keys/service.py`, add `reconcile_usage_reservation` to adjust reserved deltas on limits and items.
- [x] 1.3 In `app/modules/proxy/_service/api_key_usage.py`, add `_reconcile_websocket_request_state_reservation`.
- [x] 1.4 In `app/modules/proxy/_service/http_bridge/request_submit.py`, invoke `_reconcile_websocket_request_state_reservation` when `hard_turn_chain_advanced` is True.
- [x] 1.5 In `app/modules/proxy/_service/http_bridge/streaming.py`, invoke `_reconcile_websocket_request_state_reservation` when session anchor candidate is injected.

## 2. Regression Coverage

- [x] 2.1 Add unit test in `tests/unit/test_api_keys_service.py` verifying `reconcile_usage_reservation` updates `reserved_delta` and `ApiKeyLimit.current_value`.
- [x] 2.2 Add unit test verifying that when late anchor injection occurs in the HTTP bridge, the reservation is reconciled to conservative default input budget.
- [x] 2.3 Add test verifying that when reconciliation exceeds limits, the request fails with 429 local pre-dispatch refusal.

## 3. Validation

- [x] 3.1 Run unit tests for API keys and HTTP bridge.
- [x] 3.2 Run migration topology checks.

