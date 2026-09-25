# Capability: Responses API Compatibility

## ADDED Requirements

### Requirement: Retry Circuit Scheduled Purge Fencing
The durable bridge repository scheduled purge for stale retry circuits (`purge_retry_circuits_before`) SHALL fence each deletion against concurrent row modifications.

#### Scenario: Stale retry circuit candidate updated before deletion
- **Given** a retry circuit row that matched the stale predicate at candidate selection time with `updated_at_epoch = T0` and `admission_generation = G0`
- **When** a concurrent operation advances `admission_generation` to `G1` or updates `updated_at_epoch` to `T1`
- **Then** the deletion statement SHALL match 0 rows and SHALL NOT delete the updated retry circuit row.

---

### Requirement: Monotonic Quarantine Generations Across Removals
The in-memory bridge quarantine registry SHALL maintain strictly monotonic generation numbering per session key across entry removals and prunings.

#### Scenario: Re-quarantined key after entry removal
- **Given** a session key that was quarantined at generation `N` and subsequently removed from the active quarantine registry
- **When** the same session key is quarantined again
- **Then** the new quarantine entry SHALL receive a generation strictly greater than `N`.

---

### Requirement: Quarantine Ownership Verification on Clear
A completing request clearing quarantine on healthy completion SHALL verify that the active quarantine entry was established for the same session.

#### Scenario: Delayed completion from prior session
- **Given** an active quarantine entry established by session B
- **When** an earlier request from session A attempts to clear quarantine for the same session key
- **Then** the quarantine entry for session B SHALL NOT be cleared.
