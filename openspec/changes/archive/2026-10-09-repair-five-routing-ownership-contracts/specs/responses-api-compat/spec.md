## ADDED Requirements

### Requirement: Bridge-bypassed quota recovery projects proven retained reasoning

A bridge-bypassed full resend with turn-state ownership MUST recover from a pre-visible quota rejection when API-key-scoped durable metadata proves the exact stored prefix and complete retained answer history, the owner matches the durable row, and omission of only known redundant reasoning produces a wholly account-neutral request. The first owner attempt MUST retain the original reasoning and aliases. Only quota evidence MUST activate this projected replay; healthy owners, non-quota failures, explicit anchors, independent file ownership, unknown reasoning fields, incomplete history, and visible output MUST retain existing fail-closed ownership. A replacement MUST receive the full validated projection without stale session/turn aliases, and the rejected owner MUST remain excluded. Selection-time recovery MUST require persisted quota evidence for that same owner.

#### Scenario: Known redundant reasoning moves only after owner quota rejection

- **WHEN** a durably proven full resend retains known reasoning and the owner rejects its first attempt for quota before output
- **THEN** the replacement receives the complete account-neutral projection with reasoning omitted and stale aliases removed
- **AND** the owner's first request retains its original reasoning and aliases

#### Scenario: Healthy owners and unproven reasoning retain ownership

- **WHEN** the owner is healthy, its failure is non-quota, the durable prefix differs, or reasoning has unknown retained state
- **THEN** this projected recovery does not move the request to another account

#### Scenario: Persisted quota loss permits selection-time recovery

- **WHEN** the proven owner cannot be selected because of persisted quota state
- **THEN** the proxy can submit the same validated projection to an eligible replacement
- **AND** a non-quota selection failure does not activate the projection

### Requirement: File finalization replay eligibility covers the entire poll operation

Routed file finalization MUST NOT move to another account after any earlier poll has returned. A later individually pre-dispatch connection failure MUST retain its typed failure phase while disabling cross-account replay of the already-started finalization operation. A first-poll confirmed pre-dispatch failure on an unpinned file MUST retain existing bounded failover. A live file pin MUST remain authoritative throughout finalization.

#### Scenario: A late poll connection refusal does not relocate finalization

- **WHEN** account A returns a retry response and the next poll fails before dispatch
- **THEN** the operation surfaces the failure without polling a sibling account

#### Scenario: The first unpinned poll may still fail over

- **WHEN** the first poll of an unpinned file fails with confirmed pre-dispatch transport evidence
- **THEN** existing bounded failover can try another eligible account

### Requirement: Pre-visible quota rejection preserves ciphertext-only replacement eligibility

Before downstream output, a classified rate-limit or quota rejection MUST NOT create a new dispatch owner solely because the request retains encrypted reasoning or compaction. The exception MUST require ciphertext to be the only account-scoped retained state and the remainder of the complete request to pass the shared account-neutral replay contract. The proxy MUST forward retained ciphertext unchanged to any eligible replacement and MUST keep the rejected account excluded. Unknown fields, opaque resource references, unresolved files, explicit continuation or turn-state owners, existing dispatch owners, and single-account routing MUST remain owner-bound. Ambiguous transport failures, visible output, and code-less burst rejections MUST NOT activate this exception.

If a replacement rejects encrypted reasoning, the proxy MUST emit at most one `cross_account_encrypted_reasoning_rejected` diagnostic with request, source-account, target-account, failover-trigger, and upstream-code provenance and MUST NOT log ciphertext. Existing reservation settlement, bounded selection, lease release, and surfaced upstream errors MUST be preserved.

#### Scenario: A coded quota rejection can move retained reasoning or compaction

- **WHEN** an unanchored request whose only scoped state is retained ciphertext receives a coded HTTP 429 or first-event quota rejection before output
- **THEN** the proxy attempts an eligible replacement with unchanged ciphertext and excludes the rejected account
- **AND** reservations settle and all account leases are released

#### Scenario: Independent ownership and ambiguous execution remain bound

- **WHEN** the request also carries an independent owner, resource reference, unknown state, or visible output, or its failure is ambiguous or a code-less burst
- **THEN** this exception does not authorize cross-account replay

#### Scenario: Replacement rejection is observable without disclosing ciphertext

- **WHEN** the replacement rejects retained ciphertext with `invalid_encrypted_content` or the recognized reasoning rejection shape
- **THEN** the original rejection is surfaced and one diagnostic records the attempt provenance without ciphertext
