## MODIFIED Requirements

### Requirement: Usage-limit messages classify as account rate limits

When an upstream error envelope carries a message asserting that the account's usage limit has been reached, and its normalized error code is the `upstream_error` value a missing code normalizes to, the proxy MUST classify the failure `rate_limit`. The override MUST be limited to that code: an envelope with its own classification decision MUST retain that decision. In particular, `invalid_request_error` MUST NOT be reclassified from a usage-limit phrase in its message, because the message can quote client-supplied request content. A code-less usage-limit failure MUST NOT be treated as a burst rejection or answered with same-account backoff.

An envelope that already carries a quota or rate-limit code MUST retain its stronger classification.

Reclassification MUST NOT remove client-visible retry guidance. A rejection that would previously have surfaced with a `Retry-After` hint MUST still carry one, or a valid `error.resets_at`, when it reaches the client.

Message matching MUST be punctuation-insensitive and MUST NOT depend on the HTTP status, because upstream delivers this message both as an HTTP body and as a serialized `response.failed` frame that carries no status.

Serialized `response.failed` frames that carry code-less usage-limit messages MUST enter the same classifier and account-exclusion path before the terminal-frame gate decides the response. The absence of `upstream_error` from transport retry-code allowlists MUST NOT bypass the pool walk for those frames.

#### Scenario: Code-less usage-limit 429 rotates instead of backing off

- **WHEN** upstream answers with HTTP `429` whose body carries no error code and whose message asserts the usage limit has been reached
- **THEN** the failure is classified `rate_limit`
- **AND** the failure is not a burst rejection
- **AND** an unbound request excludes the account and continues the pool walk instead of waiting on it

#### Scenario: Code-less usage-limit response.failed frame rotates

- **WHEN** upstream serializes a pre-visible `response.failed` frame with no error code and a message asserting the usage limit has been reached
- **THEN** the streaming path classifies it with the same usage-limit evidence as the HTTP-body form
- **AND** an unbound request excludes the account and continues the pool walk before surfacing a terminal frame

#### Scenario: A request error quoting usage-limit text retains its classification

- **WHEN** upstream returns `invalid_request_error` with a message quoting client-supplied usage-limit text
- **THEN** the proxy preserves the request-error classification
- **AND** that phrase alone does not penalize or exclude the account

#### Scenario: A coded rate-limit envelope is unaffected

- **WHEN** upstream returns an envelope whose normalized error code is `rate_limit_exceeded` or `usage_limit_reached`
- **THEN** the existing rate-limit classification is preserved
- **AND** no message-based reclassification is applied

## ADDED Requirements

### Requirement: Invalid upstream reset metadata does not interrupt quota failures

The proxy MUST preserve finite integer or floating-point upstream reset metadata for account-health processing and client terminal rendering. Boolean, non-numeric, and non-finite reset values MUST be omitted without replacing the original quota code, message, or status. Each reset field MUST be validated independently. Existing numeric-string parser compatibility and account-health reset-horizon policy MUST remain enforced. Synthetic `response.failed` terminals MUST carry a valid absolute `resets_at` when available and MUST NOT invent `resets_in_seconds`.

#### Scenario: Invalid absolute reset does not discard a relative reset

- **WHEN** a quota failure carries non-finite `resets_at` and finite `resets_in_seconds`
- **THEN** account-health processing receives the relative reset without the invalid absolute reset
- **AND** the original quota failure remains available to the client

#### Scenario: Malformed resets still render a terminal failure

- **WHEN** a terminal quota failure carries a boolean, non-numeric, or non-finite absolute reset
- **THEN** terminal rendering completes with the original failure code and message
- **AND** the invalid reset field is absent

#### Scenario: Finite reset metadata survives

- **WHEN** upstream supplies finite absolute and relative reset numbers
- **THEN** both remain available to account-health processing
- **AND** a synthetic failure preserves the integer absolute reset without adding a relative reset
