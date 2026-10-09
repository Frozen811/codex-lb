## MODIFIED Requirements

### Requirement: Thread and Child-Thread Affinity

Header-only native history/notes requests SHALL evaluate `thread-id` headers for stickiness and preserve child-thread subagent placement preferences. A usable native body `context.session_id` MUST take precedence over process/thread headers for history/notes ownership. Responses and compact requests MUST retain their existing affinity classes.

#### Scenario: Thread identity routes to thread owner
- **WHEN** a native control request includes a `thread-id` header without usable body-session identity
- **THEN** it resolves thread affinity to route to the account associated with that thread

## ADDED Requirements

### Requirement: Native body session owns history and notes

Native history/notes POST operations MUST accept a JSON object, preserve its original bytes and native encrypted-argument and truncation-policy headers, and use a nonblank string `context.session_id` as a hard, separately namespaced account affinity. The first body-session operation SHALL inherit an existing soft process-session owner for that identity when eligible. Header-only compatibility requests MUST retain existing affinity behavior. A JSON object without usable body identity MUST be forwarded without inventing body-session ownership; a non-object or malformed body MUST return HTTP 400 before upstream dispatch. All native history/notes operations MUST prohibit cross-account retry after account selection, including credential refresh failures, upstream 401, quota rejection and transport failures.

#### Scenario: Body session persists across process headers
- **WHEN** native notes writes carry the same body session and different process headers
- **THEN** both writes use the same account and original body bytes

#### Scenario: First native operation inherits session owner
- **WHEN** a body-session operation has an eligible soft process owner for its session identity
- **THEN** it binds history/notes ownership to that account

#### Scenario: Native failure remains account local
- **WHEN** a selected native history/notes account fails while another account is available
- **THEN** the error is returned without dispatching the operation to the other account

#### Scenario: Invalid body is rejected
- **WHEN** a supported native POST receives malformed JSON or a non-object JSON value
- **THEN** it returns HTTP 400 with an OpenAI error envelope before upstream dispatch
