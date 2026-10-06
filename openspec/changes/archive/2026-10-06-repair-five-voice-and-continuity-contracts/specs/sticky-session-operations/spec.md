## ADDED Requirements

### Requirement: Policy-excluded continuity owners retire only when durably unavailable

For an unanchored request without file ownership or a same-owner-only full-resend proof, the HTTP bridge SHALL treat `continuity_owner_policy_conflict` as a candidate for the existing one-attempt durable owner retirement. Retirement MUST remain conditional on the exact observed durable identity, owner unavailability and inability to return before the request deadline. Policy exclusion alone MUST NOT retire a healthy owner or an owner whose reset permits timely return. Explicit response anchors and file ownership MUST remain fail closed.

#### Scenario: Excluded owner cannot return within the request budget
- **WHEN** the durable owner is unavailable beyond the deadline and selection reports the named policy conflict
- **THEN** guarded retirement permits fresh selection once without an anchor

#### Scenario: Available or near-reset owner remains bound
- **WHEN** policy excludes an active owner or an unavailable owner that can return before the deadline
- **THEN** retirement is refused and the original binding is preserved

#### Scenario: Account-owned input cannot abandon its owner
- **WHEN** the request carries a response anchor, file pin or a durable same-owner-only resend proof
- **THEN** policy conflict cannot retire the owner or dispatch to an alternate account
