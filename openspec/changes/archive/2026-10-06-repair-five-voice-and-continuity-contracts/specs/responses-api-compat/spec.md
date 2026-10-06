## ADDED Requirements

### Requirement: Empty WebSocket prewarm context survives replay classification

The proxy SHALL record the client-visible response identifier and original input-prefix evidence of an empty `generate=false` prewarm separately from generated-turn progress. A turn chained to that prewarm MUST NOT replay without its anchor unless the supplied input proves the recorded complete prefix. A delta or changed prefix MUST fail closed when upstream closes or rejects the anchor. Replay MUST retain the existing account-ownership and pre-visible-output restrictions.

#### Scenario: Delta follows an empty prewarm
- **GIVEN** an empty prewarm carried tools and developer context
- **WHEN** a chained delta loses its upstream connection before response creation
- **THEN** no unanchored delta is dispatched and the client receives a failure

#### Scenario: Full resend proves the prewarm prefix
- **WHEN** a chained request contains the recorded prewarm prefix plus fresh input
- **THEN** complete input can pass replay classification under existing ownership guards
- **AND** a modified or missing prefix fails the same proof

#### Scenario: Replayed prewarm exposes its original identifier
- **WHEN** an empty prewarm completes under a hidden upstream replay identifier
- **THEN** continuity evidence uses the identifier previously exposed to the client
- **AND** empty prewarm completion does not replace generated-turn progress

### Requirement: Durable same-owner replay preserves agent follow-ups

A prefix-verified durable HTTP bridge resend SHALL accept well-formed `agent_message` follow-ups after retained completed assistant output or a suffix exactly settling the durable pending-call manifest. Agent messages MUST NOT replace missing history, calls or outputs, or authorize unknown or malformed shapes. Dispatch SHALL preserve original item order, identifiers and encrypted content while removing a proven stale anchor only under existing operation fences and pre-visible one-shot limits. This proof MUST pin the original durable owner, including quarantined or unanchored requests, and MUST NOT authorize account-neutral replay or owner retirement.

#### Scenario: Complete same-owner agent history resumes
- **WHEN** a full resend proves the stored prefix and settled prior output followed by valid agent input
- **THEN** a fresh bridge or fenced stale-anchor retry sends the original complete input to the same account

#### Scenario: Incomplete or malformed agent history
- **WHEN** history lacks required output, a manifest call, a known manifest or a valid agent shape
- **THEN** agent input does not authorize unanchored replay

#### Scenario: Durable agent owner is unavailable
- **WHEN** the proven owner is unavailable, including on a quarantined session key
- **THEN** the request fails closed without dispatch to another account

#### Scenario: Output or operation fencing blocks retry
- **WHEN** the request has visible upstream output or lacks a required stale-anchor operation fence
- **THEN** no replacement replay is dispatched
