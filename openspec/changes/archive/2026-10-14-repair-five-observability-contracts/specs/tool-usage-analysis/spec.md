## ADDED Requirements

### Requirement: Offline tool analysis reports observed outcomes without payload disclosure
A local CLI SHALL stream explicitly supplied JSONL or gzip conversation archive files and summarize observed function/custom/computer tool calls by name. It SHALL deduplicate repeated archived copies using request and call identities, associate results with observed calls, count explicit structured errors separately, and report unknown outcomes without inferring success or failure from natural-language result text. Output MUST NOT include arguments, result text, headers or credentials. Malformed lines SHALL be counted without disclosing their contents. It MUST NOT connect to a database, provider or network or enable archive recording.

#### Scenario: Replayed call and explicit result error
- **WHEN** the same call appears in a terminal response and a later full resend with a structured error result
- **THEN** it contributes one observed call and one explicit error
- **AND** payload contents are omitted from the summary

#### Scenario: Missing result remains unknown
- **WHEN** a call has no observed result
- **THEN** its outcome is counted as unknown
- **AND** the CLI makes no claim about model correctness
