## ADDED Requirements

### Requirement: Bridge creation failure retires its owned creator

When a pending HTTP bridge session creation is evicted or failed, the bridge MUST request cancellation of the creator associated with that exact inflight slot before another creation can occupy it. A completed waiter MUST NOT exempt a still-running creator. A different replacement slot, protected handoff or currently executing creator MUST retain its existing task ownership. Existing cleanup MUST release predecessor resources without closing a registered successor or changing its durable ownership.

#### Scenario: Creation failure removes a running predecessor
- **WHEN** a matching inflight creation fails while its creator is awaiting upstream work
- **THEN** the predecessor receives cancellation and its slot is removed
- **AND** a subsequent request can establish a replacement without predecessor dispatch or leaked leases

#### Scenario: Waiter is complete while creator is running
- **WHEN** the matching waiter has already completed but its creator is still running
- **THEN** failure still requests cancellation of the creator

#### Scenario: Replacement and handoff ownership remain intact
- **WHEN** failure targets a superseded slot, a protected handoff or the current creator
- **THEN** it does not cancel another creator or itself

### Requirement: Late bridge anchors keep admission budgets consistent

Before dispatch of a request whose opaque continuation anchor was added after API-key reservation, the bridge MUST reconcile its persisted reservation using the conservative anchored-input budget. Successful reconciliation MUST retain that same budget in the request's local admission state so subsequent stream-lease acquisition cannot reuse the earlier self-contained estimate. A rejected reconciliation MUST prevent upstream dispatch and release the reservation through the existing settlement lifecycle, preserving the external auth or rate-limit error.

#### Scenario: Late anchor grows the active reservation
- **WHEN** the bridge adds an opaque anchor to a previously self-contained reserved request
- **THEN** its active reservation and local admission estimate reflect the anchored budget before upstream send

#### Scenario: Late anchor exceeds the API-key limit
- **WHEN** the original request fits the key limit but its conservative anchored estimate does not
- **THEN** the request receives the documented rate-limit envelope without upstream dispatch
- **AND** the original reservation is released without leaked reserved quota

#### Scenario: Reconciliation fails authentication
- **WHEN** late-anchor reconciliation finds the API key invalid
- **THEN** the original auth error is preserved and no upstream request is sent
