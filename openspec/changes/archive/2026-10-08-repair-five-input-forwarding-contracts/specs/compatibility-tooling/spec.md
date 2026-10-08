## ADDED Requirements

### Requirement: Responses fixture sanitization preserves tool continuity evidence

The fixture sanitizer MUST preserve optional boolean async markers on function_call and custom_tool_call items, retain their absence when omitted, and preserve paired call IDs across typed outputs. It MUST retain the known tool_search_call and tool_search_output wire fields, including client/server execution and loaded tool declarations, while redacting captured query text and identifiers through the existing deterministic sanitizer. Adding async marker support MUST NOT widen the field allowlists of tool outputs or unrelated input item types.

#### Scenario: Optional async marker remains reproducible
- **WHEN** a captured function/custom call has an omitted, false or true async marker
- **THEN** the sanitized fixture retains that optional marker state and its matching output pairing without preserving captured call text

#### Scenario: Loaded search tools remain testable after sanitization
- **WHEN** a fixture includes a completed tool-search call and an output with loaded tools
- **THEN** sanitization preserves the paired structure and known declarations with deterministic redaction and the fixture shape guard recognizes both item types
