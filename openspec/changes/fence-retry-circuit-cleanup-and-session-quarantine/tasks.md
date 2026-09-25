# Tasks: Fence Retry Circuit Cleanup and Isolate Session Quarantine

## Tasks

- [x] 1. Update `DurableBridgeRepository.purge_retry_circuits_before` in `app/modules/proxy/durable_bridge_repository.py`:
  - Select `updated_at_epoch` and `admission_generation` in the candidate query.
  - Add `HttpBridgeRetryCircuit.updated_at_epoch == updated_at_epoch` and `HttpBridgeRetryCircuit.admission_generation == admission_generation` to the `delete` where-clause.
- [x] 2. Update `app/modules/proxy/_service/http_bridge/quarantine.py`:
  - Add service-level monotonic generation tracking for session keys (`_http_bridge_quarantine_generations`).
  - Add `session_id: str | None = None` and `session_identity: int | None = None` to `_HTTPBridgeQuarantineEntry` and populate them in `_quarantine_http_bridge_session`.
  - In `_clear_http_bridge_quarantine`, use monotonic generations to prevent stale session clears.
- [x] 3. Write unit tests:
  - In `tests/unit/test_bridge_ring_lifecycle.py`: Test that `purge_retry_circuits_before` does not delete a row whose `admission_generation` or `updated_at_epoch` changed between select and delete.
  - In `tests/unit/test_proxy_http_bridge.py`: Test that `_clear_http_bridge_quarantine` does not clear an entry when monotonic generations advance across entry removals.
- [x] 4. Run tests and verify all pass.
