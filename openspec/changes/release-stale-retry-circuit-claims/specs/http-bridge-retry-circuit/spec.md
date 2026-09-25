# HTTP Bridge Retry Circuit Specification

## Retry Claim Release and Expiry

- **GIVEN** a request claims a durable retry circuit admission generation
  **WHEN** the request exits before attempting an upstream send (`response_create_attempt_count == 0`)
  **THEN** the durable claim SHALL be released by reverting the `admission_generation` under the lineage fence.

- **GIVEN** a retry circuit claim in the durable store
  **WHEN** a subsequent request checks if a remote probe holds the lease (`_http_bridge_claim_miss_shows_remote_probe`)
  **THEN** the claim SHALL NOT be considered active if more than `_HTTP_BRIDGE_RETRY_CIRCUIT_HALF_OPEN_LEASE_SECONDS` has elapsed since the lineage epoch.

- **GIVEN** an in-memory half-open lease is claimed during admission
  **WHEN** the submit flow exits or is cancelled before upstream send
  **THEN** the in-memory lease SHALL be released and the cooldown marker restored so subsequent requests can re-claim the probe.
