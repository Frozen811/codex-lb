# Tasks: release-stale-retry-circuit-claims

- [x] 1. Durable Bridge Repository and Coordinator
  - [x] 1.1 Add `release_retry_circuit_claim` to `DurableBridgeRepository` in `app/modules/proxy/durable_bridge_repository.py`.
  - [x] 1.2 Add `release_retry_circuit_claim` to `DurableBridgeCoordinator` in `app/modules/proxy/durable_bridge_coordinator.py`.
- [x] 2. Proxy HTTP Bridge Service Integration
  - [x] 2.1 Add `_release_http_bridge_retry_circuit_claim` to `app/modules/proxy/_service/http_bridge/retry_circuit.py`.
  - [x] 2.2 Track claimed durable generation on `request_state` and release it in `finally` blocks when `response_create_attempt_count == 0` in `app/modules/proxy/_service/http_bridge/request_submit.py`.
  - [x] 2.3 Bound remote probe lease validity by `_HTTP_BRIDGE_RETRY_CIRCUIT_HALF_OPEN_LEASE_SECONDS` in `_http_bridge_claim_miss_shows_remote_probe`.
- [x] 3. Tests & Verification
  - [x] 3.1 Unit tests in `tests/unit/test_durable_bridge_sessions.py` for `release_retry_circuit_claim`.
  - [x] 3.2 Unit tests in `tests/unit/test_proxy_http_bridge.py` for unattempted claim release and lease expiration.

