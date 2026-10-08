## ADDED Requirements

### Requirement: Post-submit cooldown preserves an owned upstream terminal

After an HTTP bridge request has been submitted, the proxy MUST NOT replace an upstream terminal already claimed for settlement or observed for that request with a synthetic cooldown refusal solely because the downstream queue is still empty. It MUST preserve the upstream terminal and existing exactly-once reservation settlement, ownership, and retry-circuit accounting. A submitted request subject to cooldown suppression without terminal evidence, response events, or queued output MUST retain the existing fail-closed refusal and detach cleanup. Existing verified stale-anchor recovery policy MUST remain unchanged. This rule MUST NOT authorize another upstream send or cross-account replay.

#### Scenario: Incomplete terminal opens its own circuit before publication

- **WHEN** an upstream reason-only incomplete is claimed for settlement and opens the durable circuit before its downstream payload is enqueued
- **THEN** the admitted request receives the original incomplete terminal
- **AND** the original circuit strike and reservation settlement remain effective
- **AND** admission and verified recovery policy for later requests remain unchanged

#### Scenario: Terminal observation survives settlement completion

- **WHEN** a submitted request has an observed upstream terminal timestamp but its queue is not yet readable
- **THEN** the post-submit cooldown check does not replace that terminal with a synthetic refusal

#### Scenario: No terminal evidence still fails closed

- **WHEN** cooldown becomes visible after submit and the request has no claimed or observed terminal, response events, or queued output
- **AND** the request does not qualify for the existing verified stale-anchor recovery exception
- **THEN** the proxy retains its existing cooldown refusal
- **AND** detaches the submitted request and releases its owned resources
