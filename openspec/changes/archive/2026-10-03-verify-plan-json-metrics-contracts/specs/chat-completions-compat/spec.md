## MODIFIED Requirements

### Requirement: Map chat requests to Responses wire format

The service MUST map chat messages into the Responses request format by merging `system`/`developer` content into `instructions` and forwarding all other messages as `input`. When JSON object mode is selected by `response_format` (string or object) or equivalent `text.format.type`, the service MUST preserve each `system`/`developer` message mentioning JSON, case-insensitively, as a `developer` input message in its original relative position. Other instruction messages MUST continue to move into `instructions`. The preserved prefix MUST NOT depend on later user messages. Tool definitions MUST be normalized to the Responses tool schema, and `tool_choice`, `reasoning_effort`, and `response_format` MUST be mapped consistently. Unsupported fields MUST not be silently ignored if they change behavior.

#### Scenario: System message normalization
- **WHEN** the client sends a system message followed by a user message without JSON object mode
- **THEN** the service maps system content to instructions and user content to input

#### Scenario: JSON object response format preserves instruction-role messages
- **WHEN** a system or developer message mentions JSON and JSON object mode is selected with either supported format representation
- **THEN** the message stays in input as a developer message in its original relative position
- **AND** its content is absent from top-level instructions while unrelated instructions are hoisted

#### Scenario: Equivalent JSON controls preserve prefix across turns
- **WHEN** a later user message is appended to a JSON object request
- **THEN** the earlier developer input prefix remains identical for response_format and text.format

#### Scenario: Tool choice values
- **WHEN** the client sets tool_choice to none, auto, or required
- **THEN** the service forwards the value consistently in the mapped Responses request
