# Release stale retry circuit claims

## Why
When an HTTP bridge request admits a half-open probe and claims the durable retry circuit generation in `HttpBridgeRetryCircuit` (or an in-memory lease), but the request exits before attempting an upstream send (due to poisoned anchor rejection, ledger refusal, connection drop, client cancellation, or worker exit), the claim remains recorded in the database.
Because `HttpBridgeRetryCircuit.admission_generation` remains incremented while `updated_at_epoch` and `consecutive_failures` remain at threshold, subsequent requests checking `_http_bridge_claim_miss_shows_remote_probe` observe an advanced generation and assume a remote probe holds the lease, suppressing requests for up to 600s (or up to the 7,260s retention TTL) while callers receive `Retry-After: 1`.

## What changes
1. **Durable Claim Release**: Add `release_retry_circuit_claim` to `DurableBridgeRepository` and `DurableBridgeCoordinator` to decrement `admission_generation` back and reset cooldown under the lineage fence (`updated_at_epoch == expected_updated_at_epoch`).
2. **Submit-Time Cleanup**: In `_submit_http_bridge_request` and `_retry_http_bridge_precreated_request`, ensure that any claimed durable generation and in-memory half-open lease are released in `finally` blocks if `response_create_attempt_count == 0` (the probe never flew).
3. **Lease Liveness Check**: In `_http_bridge_claim_miss_shows_remote_probe`, ensure that an advanced admission generation is only treated as an active remote probe if the claim is within `_HTTP_BRIDGE_RETRY_CIRCUIT_HALF_OPEN_LEASE_SECONDS` (600s). Once the lease window elapses, the claim is treated as expired/stale rather than suppressing traffic indefinitely.
