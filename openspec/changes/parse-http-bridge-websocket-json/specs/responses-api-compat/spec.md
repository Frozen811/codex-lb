## ADDED Requirements

### Requirement: HTTP bridge parses complete WebSocket JSON documents

The HTTP Responses bridge MUST interpret upstream text messages as complete
JSON objects, independent of indentation, LF/CRLF formatting, or surrounding
JSON whitespace. Native-interpreted and opaque frames MUST have equivalent
classification and correlation. Conversion to SSE MUST retain a complete valid
JSON object. Actual HTTP SSE parsing MUST remain unchanged.

#### Scenario: Early multiline error is delivered

- **GIVEN** one request awaits response creation
- **WHEN** upstream sends a formatted JSON validation error
- **THEN** the client receives the original code, type, and parameter through the existing HTTP 400 or committed SSE error contract
- **AND** pending state settles without a formatting-induced retry, timeout, quarantine, or account penalty
- **AND** the next valid request can use the bridge

#### Scenario: Formatted successful lifecycle

- **WHEN** lifecycle and output messages contain indentation or CRLF
- **THEN** the bridge preserves their event ordering, response correlation, and valid downstream SSE

#### Scenario: Invalid data remains unclassified

- **WHEN** a frame is malformed JSON, a non-object JSON value, or SSE-framed text
- **THEN** it does not manufacture response identity or terminal evidence
- **AND** existing pending-request safety remains authoritative
