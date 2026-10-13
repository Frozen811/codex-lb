## ADDED Requirements

### Requirement: Complete durable bridge replay starts at the root

The HTTP bridge SHALL persist each generated root turn in its durable operation ledger before upstream dispatch, including its original input and a null parent. Independent unanchored turns MUST retain distinct operation identities. Registration MUST obey the existing owner, admission, exact-frame size and interruption cleanup fences.

#### Scenario: Root and tool continuation form a complete chain
- **WHEN** a root response produces a tool call and a continuation supplies its output
- **THEN** durable replay retains the root input, terminal tool call, continuation output and final answer in order without duplicate echoed tool items

#### Scenario: Independent roots contain identical prompts
- **WHEN** two unanchored turns supply the same body
- **THEN** each turn dispatches and records its own operation rather than replaying the first turn

#### Scenario: Root registration or dispatch is refused
- **WHEN** the owner fence, payload limit or admission fails before a root dispatch
- **THEN** no upstream request is sent and no newly created submitted operation remains orphaned

#### Scenario: Independently proven output-free root retry
- **WHEN** existing replay policy independently permits an output-free root retry
- **THEN** predecessor lifecycle writes are drained and discarded before the retry resets its transcript under the currently fenced session account
- **AND** an acknowledged predecessor requires its captured response identity, while an unacknowledged predecessor requires an absent response identity and empty spool
- **AND** parent anchors, completed operations, mismatched response identities and stale owners refuse this reset

### Requirement: Durable replay requires matching complete terminal evidence

A durable transcript SHALL be exposed for reconstruction only when each turn has exactly matching response identity, a complete successful or incomplete terminal outcome and consistent observed output-item lifecycles. Missing done evidence for an observed added item, conflicting output identities, malformed terminal output or a chain crossing authorization scopes MUST fail closed. Item-done output MAY supply terminal material when an upstream terminal omits its output list. Existing byte, item, turn, account-neutrality and parent-chain bounds MUST remain enforced.

#### Scenario: Added output item lacks its done event
- **WHEN** an event spool terminates while an observed output item has no matching done evidence
- **THEN** that spool cannot authorize durable reconstruction even if the terminal repeats the item

#### Scenario: Terminal identity or scope does not match
- **WHEN** a stored terminal names another response or a parent belongs to another API-key scope
- **THEN** no replay transcript is returned

#### Scenario: Incomplete terminal omits output
- **WHEN** every observed output item completes and the matching incomplete terminal omits its output field
- **THEN** the completed items remain available for bounded replay reconstruction
