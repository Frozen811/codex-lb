## MODIFIED Requirements

### Requirement: Hard continuity owner lookup fails closed

When a request depends on hard continuity ownership, the service MUST fail
closed if owner or ring lookup errors prevent safe pinning. The service MUST NOT
continue with account selection that bypasses hard owner enforcement. A direct
WebSocket continuation already attached to its required open owner socket MUST
NOT be failed solely because a new per-turn selection attempt temporarily
excludes that owner.

For subscription continuations after a successful previous-response owner lookup returns no owner, HTTP,
compact and direct WebSocket transports MUST evaluate possible subscription
owners using the API key's assigned account scope, or the complete subscription
pool for an unscoped request. Health, quota, plan and model eligibility MUST NOT
reduce this ownership candidate set. Exactly one possible owner MUST be pinned
through normal required-owner admission; zero or multiple candidates and
candidate-listing errors MUST fail closed with the existing retryable
previous-response error. An explicitly enabled empty assignment scope MUST
remain empty. Codex session affinity MUST NOT bypass ambiguous or failed
previous-response owner resolution. Ownership evidence from turn-state and files MUST retain existing
conflict checks. A fallback candidate MUST NOT grant permission for new dispatch
to a paused or otherwise unavailable account or for cross-account failover.
Candidate information MUST remain readable after repository-session teardown;
internal session-lifecycle failures MUST NOT escape as unhandled HTTP 500 errors.

#### Scenario: websocket previous-response owner lookup errors

- **WHEN** a websocket or HTTP fallback follow-up includes `previous_response_id`
- **AND** owner lookup errors prevent determining the required owner
- **THEN** the service returns a retryable OpenAI-format error
- **AND** it does not continue on an unpinned account

#### Scenario: bridge owner or ring lookup errors for hard continuity keys

- **WHEN** an HTTP bridge request uses a hard continuity key such as turn-state, explicit session affinity, or `previous_response_id`
- **AND** owner or ring lookup errors prevent proving the correct bridge owner
- **THEN** the service returns a retryable OpenAI-format error
- **AND** it does not create or recover a local bridge session on the current replica

#### Scenario: required owner differs from the open WebSocket account

- **WHEN** a direct WebSocket follow-up resolves to an owner different from the currently open upstream account
- **THEN** the service retires the current upstream socket
- **AND** reconnects the unchanged anchored request to the required owner
- **AND** it does not forward any `x-codex-turn-state` associated with the retired account, whether supplied by the client or learned upstream

#### Scenario: required owner matches the healthy open WebSocket account

- **WHEN** a direct WebSocket follow-up resolves to the currently open owner
- **THEN** the service sends it on that socket without a new selector-based eligibility check

#### Scenario: previous-response owner lookup miss fails closed even when single account matches model

- **WHEN** a follow-up carries `previous_response_id` and its owner lookup successfully misses
- **AND** several subscription accounts are in scope but only one supports the model or is currently routable
- **THEN** the service returns `previous_response_owner_unavailable`
- **AND** it does not dispatch to the model-matching or routable account

#### Scenario: sole possible owner survives session teardown

- **WHEN** a previous-response lookup successfully misses and the allowed subscription pool contains exactly one account
- **AND** its candidate-listing repository session has finished
- **THEN** HTTP, compact and direct WebSocket requests pin that owner through normal admission
- **AND** forward the unchanged `previous_response_id` if admission permits dispatch

#### Scenario: assigned scope excludes unrelated accounts

- **WHEN** a previous-response lookup successfully misses for a key assigned to exactly one account
- **AND** additional accounts exist outside that assignment
- **THEN** the assigned account is the sole fallback candidate
- **AND** no account outside the key's scope is selected

#### Scenario: empty scope or listing failure

- **WHEN** an owner lookup successfully misses but the assigned scope is empty or candidate listing fails
- **THEN** the request returns the retryable previous-response owner error
- **AND** no upstream dispatch occurs

#### Scenario: paused candidates remain ownership candidates

- **WHEN** a previous-response lookup misses in a scope containing an active account and a paused account
- **THEN** both accounts remain possible owners
- **AND** the request fails closed without dispatch

#### Scenario: sole paused owner is refused by admission

- **WHEN** a previous-response lookup misses and the sole scoped candidate is paused
- **THEN** new dispatch is refused by required-owner admission
- **AND** no alternate account is selected
