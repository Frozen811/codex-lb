## ADDED Requirements

### Requirement: HTTP bridge incomplete reasons preserve retry accounting eligibility

An HTTP bridge `response.incomplete` terminal with `incomplete_details.reason = stream_incomplete` SHALL count through the existing attempt-scoped retry circuit when no explicit response error is present. An explicit response error SHALL take precedence. Raw and interpreted terminals SHALL retain the same accounting, payload, request-log and account-health behavior. Soft affinity, observed nonterminal output, prewarm, skipped logs, safe replay and non-transport reasons SHALL retain their existing exclusions. Duplicate handling of one send attempt SHALL NOT add another strike.

#### Scenario: Reason-only incomplete terminal

- **WHEN** an eligible raw or interpreted incomplete terminal identifies stream_incomplete only in incomplete_details
- **THEN** its send attempt contributes one durable circuit strike and its terminal payload is preserved

#### Scenario: Explicit error and eligibility exclusions

- **WHEN** an incomplete terminal has an explicit unrelated error or its request is excluded by the existing circuit policy
- **THEN** the incomplete reason does not bypass that error or exclusion

### Requirement: HTTP bridge persisted cooldown absence does not manufacture probes

A missing, zero, negative or already elapsed persisted cooldown SHALL NOT manufacture a local cooldown transition or a half-open probe when no positive local cooldown transition exists. Repeated loads of the same durable episode SHALL preserve a probe already owned by local active work. A positive local cooldown that expires SHALL admit at most one half-open probe under the existing lease policy.

#### Scenario: Repeated elapsed cooldown loads

- **WHEN** the bridge repeatedly loads a row whose cooldown is absent or already elapsed
- **THEN** normal admission remains available without a manufactured local probe

#### Scenario: Local probe remains active

- **WHEN** a real local cooldown expires and its admitted probe reloads the same durable episode
- **THEN** a sibling remains suppressed while that local lease is active

### Requirement: HTTP bridge undispatched claim receipts survive caller cancellation

When a verified stale-anchor replay claims a durable circuit generation, the proxy SHALL own and await the claim through the existing bounded acquisition timeout, including time spent waiting for its local key lock. Caller cancellation SHALL be deferred until the claim returns or that bound is reached. A successful claim SHALL be attached to the request before cancellation is propagated, and submission cleanup SHALL attempt fenced release if no upstream send was attempted. The claim receipt SHALL reflect the winning write transaction, including the inserted epoch when no prior circuit row existed; a post-commit successor SHALL NOT replace that receipt. Durable release SHALL NOT clear another request's local half-open lease. An attempted or ambiguous send SHALL retain its claim protection.

#### Scenario: Cancellation after claim commit before receipt delivery

- **GIVEN** the coordinator committed a claim but has not returned its receipt
- **WHEN** the requesting task is cancelled and the bounded claim completes
- **THEN** the receipt is retained, no upstream send occurs and submission attempts fenced release before cancellation completes

#### Scenario: Late release with replacement local lease

- **GIVEN** a newer request owns a local half-open probe
- **WHEN** an older durable claim release succeeds, is fenced out or fails
- **THEN** the newer local probe and cooldown remain unchanged

#### Scenario: Ambiguous dispatch keeps claim protection

- **WHEN** an upstream send may have started before the request exits
- **THEN** cleanup does not release that request's durable claim as undispatched

#### Scenario: Claim inserts a new row or a successor claims after commit

- **WHEN** a claim inserts a previously absent row or another claim advances its generation immediately after commit
- **THEN** the returned receipt identifies only the winning claim and cleanup remains fenced against the successor
