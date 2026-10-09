# bridge-ring-membership Specification

## Purpose
Governs how replicas join, stay in, and leave the shared bridge ring that routes hard-affinity HTTP bridge requests to the owning replica. Sibling replicas must converge on the same view of which instances are alive, so a replica registers before serving bridge traffic, heartbeats on a fixed cadence, ages its row on shutdown rather than deleting it, and dead rows are eventually purged.

## Requirements

### Requirement: Replicas register in the bridge ring before serving bridge traffic
Each replica MUST register its instance id (and advertised endpoint when configured) in the shared `bridge_ring_members` table before hard-affinity HTTP bridge requests are admitted. While registration is incomplete in a multi-replica deployment, hard-affinity bridge requests MUST wait for registration up to the configured connect timeout and fail with a retryable `bridge_owner_unreachable` error when the wait expires.

#### Scenario: Hard-affinity request before registration completes
- **WHEN** a hard-affinity HTTP bridge request arrives on a replica whose ring registration has not completed
- **AND** the deployment requires cluster registration (multi-instance ring or non-loopback advertise URL)
- **THEN** the request waits for registration up to the configured connect timeout
- **AND** it fails with a retryable `bridge_owner_unreachable` error if registration is still incomplete

### Requirement: Ring membership is maintained by periodic heartbeats
Each registered replica MUST refresh its ring row via an upsert heartbeat every 10 seconds so sibling replicas observing the shared table converge on the same active-member view. Ring readers MUST treat a member as active only when its heartbeat is within the 30-second stale threshold.

#### Scenario: Missed heartbeats age a member out of the active ring
- **WHEN** a replica stops heartbeating for longer than the stale threshold
- **THEN** ring readers no longer include that instance in the active member list
- **AND** owner-endpoint resolution for that instance returns no endpoint

#### Scenario: Heartbeat recovers a row removed by a sibling
- **WHEN** a replica's ring row was deleted or aged by another process
- **THEN** the replica's next heartbeat re-upserts the row with a fresh timestamp

### Requirement: Shutdown ages the ring row instead of deleting it
On graceful shutdown a replica MUST age its ring row's heartbeat close to the stale threshold rather than deleting the row, leaving a short grace window (heartbeat interval plus 5 seconds) during which sibling workers sharing the same instance id can refresh the row while a fully terminating pod still ages out quickly.

#### Scenario: Terminating pod leaves a short grace window
- **WHEN** a replica shuts down gracefully
- **THEN** its ring row's heartbeat is set so the member ages out after the shutdown grace window
- **AND** the row is not deleted, so a surviving sibling worker's next heartbeat can restore it

### Requirement: Dead ring rows are purged
The background cleanup loop MUST delete `bridge_ring_members` rows whose heartbeat is older than 24 hours so rows for permanently departed replicas do not accumulate. Rows within the retention window MUST NOT be deleted so shutdown stale-aging and restart recovery keep working.

#### Scenario: Cleanup removes long-dead members and keeps recent ones
- **WHEN** the cleanup loop runs
- **AND** one ring row's heartbeat is older than 24 hours while another's is recent
- **THEN** the old row is deleted
- **AND** the recent row is preserved

### Requirement: Bridge signing uses the configured shared encryption key

Internal bridge request signing and verification MUST use the configured encryption key. A nonempty `CODEX_LB_ENCRYPTION_KEY` MUST take precedence over `CODEX_LB_ENCRYPTION_KEY_FILE` without reading or creating a file key. With no environment key, the configured file key MUST be used. Replicas sharing the effective key MUST accept each other's authentic forwards; a replica with a different effective key MUST reject the signature before forwarding upstream.

#### Scenario: Shared environment key and distinct file keys
- **WHEN** two replicas share an environment key and have distinct configured file keys
- **THEN** the receiver accepts the signed request using the environment key and the file keys remain unchanged

#### Scenario: File-only shared key
- **WHEN** replicas have no environment key and share the configured file key
- **THEN** the receiver accepts the signed request

#### Scenario: Mismatched effective key
- **WHEN** the receiver's effective key differs from the signing replica's key
- **THEN** signature verification refuses the forward

### Requirement: Optional maintenance cannot block ring renewal
After registration, periodic ring renewal MUST be independent of durable ownership reconciliation, stale-operation cleanup, idle-session sweeping and cap-partition refresh. Each optional phase MUST have at most one in-flight invocation, MUST retry ordinary failures on its next cadence and MUST stop starting work after observing shutdown. Ring database operations MUST use background connection admission rather than the request pool. Shutdown MUST stop all phase owners before stale marking and engine disposal; cancellation-resistant owners MUST remain visible to clean-shutdown checks.

#### Scenario: One maintenance phase is blocked
- **WHEN** a durable reconciliation pass cannot complete
- **THEN** heartbeat, idle sweeping, stale-operation cleanup and cap refresh continue independently
- **AND** no second reconciliation pass starts while the first is pending

#### Scenario: A maintenance pass fails
- **WHEN** one optional phase raises an ordinary exception
- **THEN** other phase owners continue and the failed phase retries on its next cadence

#### Scenario: Shutdown interrupts independent phase owners
- **WHEN** shutdown begins with optional maintenance in flight
- **THEN** each phase stops cooperatively within the existing bounded stop policy
- **AND** incomplete work prevents a clean-shutdown claim
