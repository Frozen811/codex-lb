## ADDED Requirements

### Requirement: Continuation classification consumes preceding tool call occurrences

HTTP bridge classification MUST treat an output as self-contained only when a preceding, unconsumed call of the corresponding protocol has the same nonempty call identifier. Reused identifiers MUST be matched in occurrence order. An unmatched output MUST retain its continuation semantics through request normalization and owner forwarding; it MUST NOT authorize dropping a prior response anchor. Raw string and single-item inputs MUST remain single turns irrespective of serialized length.

#### Scenario: A second output cannot reuse an already consumed call
- **WHEN** input includes one call and two outputs with its identifier
- **THEN** the bridge treats the body as a continuation and preserves its required anchor

#### Scenario: Repeated complete pairs remain self-contained
- **WHEN** input includes repeated call/output pairs with the same identifier
- **THEN** each output consumes its own preceding call and the complete body remains a full resend

#### Scenario: Protocols do not share call occurrences
- **WHEN** a function output follows only a computer or custom call with the same identifier
- **THEN** the body remains a continuation

#### Scenario: Normalization preserves single-turn meaning
- **WHEN** a raw string near the historical size threshold becomes one message or is internally forwarded
- **THEN** it remains a single turn and does not authorize removal of a prior anchor
