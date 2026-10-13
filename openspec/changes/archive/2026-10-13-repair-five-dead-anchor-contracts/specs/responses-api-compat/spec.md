## ADDED Requirements

### Requirement: Dead-owner recovery horizons reflect the owner's status

When an HTTP Responses bridge request has proven its continuity owner unavailable, retirement MUST treat a reset timestamp as evidence of automatic recovery only when the owner is rate-limited or quota-exceeded. A paused, deactivated or confirmed-unusable reauthentication owner MUST NOT be kept solely because a stored reset timestamp falls within the request budget. Retirement MUST retain the account-status lock, conditional status check and expected-owner check, and MUST NOT mutate stored reset metadata. An active or recovered owner MUST NOT be retired.

#### Scenario: Administrative unavailability has an incidental near reset
- **WHEN** a request encounters a paused or deactivated continuity owner with a reset timestamp inside its budget
- **THEN** that timestamp does not prevent conditional owner retirement
- **AND** the stored account status and reset timestamp remain unchanged

#### Scenario: Unusable reauthentication has an incidental near reset
- **WHEN** selection has proven a reauthentication owner's credentials unusable and its stored reset timestamp is inside the request budget
- **THEN** the timestamp does not defer conditional retirement

#### Scenario: Quota owner can return within the budget
- **WHEN** a rate-limited or quota-exceeded owner has a reset timestamp before the recovery deadline
- **THEN** the owner is retained for existing bounded recovery

#### Scenario: Quota owner has no usable horizon
- **WHEN** a rate-limited or quota-exceeded owner's reset timestamp is absent or at or after the recovery deadline
- **THEN** the unavailable owner is eligible for conditional retirement

#### Scenario: Ownership or status changed
- **WHEN** the expected owner no longer owns the session or its status recovered before retirement
- **THEN** the current healthy or different owner is preserved

### Requirement: Proven-dead client anchors receive actionable terminal rejection

When an HTTP bridge request carries a client-supplied response anchor owned by an account that cannot return within its budget, the bridge MUST conditionally retire that owner and deliver HTTP 404 `bridge_previous_response_not_found` with a remedy to resend the full conversation history or start a new conversation. The rejection MUST remain unmasked on canonical and equivalent HTTP paths, including trailing slash aliases, and MUST NOT independently authorize raw-HTTP replay. Repeated retirement attempts for the same unavailable owner MUST report the existing retirement without rewriting its marker. An eligible subsequent anchor-free full-history request MUST be able to bind to a healthy account; this MUST NOT make account-owned files or encrypted state portable.

#### Scenario: Client anchor on a dead owner
- **WHEN** a client resumes a bridged thread using its own anchor on a paused owner
- **THEN** it receives the actionable 404 instead of a retryable owner-unavailable failure

#### Scenario: Anchor-free recovery on the same thread
- **WHEN** the client follows the rejection with eligible full history and no anchor on the same thread
- **THEN** a healthy owner can serve the request
- **AND** the complete supplied history is preserved

#### Scenario: Duplicate retirement
- **WHEN** a duplicate request observes the same already-retired unavailable owner
- **THEN** retirement reports success without rewriting the original scope or timestamp

#### Scenario: Repeated client anchor after retirement
- **WHEN** the client repeats its anchored request and a durable retirement marker hides the former owner from normal lookup
- **THEN** the bridge preserves the actionable 404 verdict instead of returning a retryable owner-lookup failure
- **AND** it neither redispatches the anchor nor rewrites the retirement marker

#### Scenario: File ownership still constrains recovery
- **WHEN** a request also carries an uploaded file owned by the unavailable account
- **THEN** recovery does not forward the file through another account

### Requirement: Submit-time abandonment tombstones retire exact proxy anchors

When submission rejects a proxy-injected response anchor after adopting an abandonment tombstone, the bridge MUST retire that exact anchor from matching live and durable continuity carriers while preserving the existing 404 `bridge_previous_response_not_found` refusal. Retirement MUST retain the tombstone guarding incomplete delta requests, preserve successor continuity and leave client-supplied anchors untouched. Cleanup failure MUST NOT replace the selected public refusal; cancellation MUST retain the existing lifecycle cleanup policy.

A local refusal proven to precede request publication and dispatch MUST preserve its selected error through outer recovery handling. It MUST NOT trigger transparent upstream replay or a missing-operation-fence error merely because the original request contained eligible full history.

#### Scenario: First refusal clears both matching carriers
- **WHEN** a proxy-injected anchor reaches submission after its abandonment tombstone is adopted
- **THEN** the bridge returns the existing 404 and retires the matching live and durable anchor

#### Scenario: Full resend escapes the tombstone
- **WHEN** the client resends complete eligible history without an anchor after that retirement
- **THEN** normal admission can dispatch the complete history without reinjecting the rejected anchor

#### Scenario: Delta-only follow-up remains refused
- **WHEN** an incomplete delta follows that retirement without a response anchor
- **THEN** the abandonment tombstone continues refusing context-free dispatch

#### Scenario: A successor is preserved
- **WHEN** another request advances continuity before retirement finishes
- **THEN** only the rejected anchor is considered for cleanup and the successor survives

#### Scenario: Client anchor is preserved
- **WHEN** the request supplied its own anchor rather than receiving proxy injection
- **THEN** the submit-time proxy-anchor cleanup does not clear or rewrite that client anchor

#### Scenario: Cleanup fails
- **WHEN** exact-match anchor cleanup encounters a transient failure
- **THEN** the selected public refusal remains intact and existing bounded cleanup retains its denial fence
