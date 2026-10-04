## ADDED Requirements

### Requirement: Metrics startup preserves shared operator logging

Starting the metrics listener MUST preserve process logging levels, handlers, redacting formatters, and configured file output. At info and debug levels, access records from both the primary listener and metrics scrapes MUST remain observable with the selected text or JSON format, including file paths with spaces. URL userinfo redaction MUST remain effective in both streams and files after metrics startup.

JSON access records MUST contain the observed client, request line, and numeric HTTP status. Optional tracing failures MUST NOT recursively re-enter tracing enrichment or prevent JSON debug startup.

#### Scenario: Both listeners continue redacted file and stream logging
- **WHEN** the CLI starts with metrics enabled and a log file, then both listeners receive requests with credentialed URLs in the query
- **THEN** both access records appear in stream and file with the selected format
- **AND** neither output contains the credentials

#### Scenario: JSON access records retain request evidence
- **WHEN** either listener emits a JSON access record for a request
- **THEN** the record contains its client, redacted method/path/protocol, and numeric HTTP status

#### Scenario: Optional tracing is unavailable during JSON debug startup
- **WHEN** the CLI starts in JSON debug mode without the tracing extra
- **THEN** both listeners become reachable and logging emits no recursion failure
