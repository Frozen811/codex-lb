## MODIFIED Requirements

### Requirement: Secret-pattern redaction stays on the current line

Keyed, bearer, basic, authorization, JSON, and Python-repr secret patterns
MUST be applied independently to each CR/LF-delimited line of rendered log
text. A match MUST NOT consume CR or LF or any text from a following line.
Unterminated JSON secret values MUST be redacted through the end of the
current line. A Bearer credential MUST treat a glued `:` tail on the same
line as credential material. Same-line comma and ampersand separators MUST
keep their existing truncation behavior except within an explicit Authorization or Proxy-Authorization
field, whose value MUST follow the authorization-field redaction requirement. Records below WARNING MUST still
skip these keyed patterns.

#### Scenario: Authorization does not swallow the next traceback line

- **GIVEN** a WARNING or higher record whose exception text contains
  `authorization=Basic X` followed by a newline and `status=failed`
- **WHEN** the text or JSON formatter renders the record
- **THEN** the Basic credential is replaced with `[REDACTED]`
- **AND** the following line still contains `status=failed`

#### Scenario: Unterminated JSON secret is redacted through end of line

- **GIVEN** a WARNING or higher record contains `{"token":"abc` with no
  closing quote before the line ending, then a following `safe diagnostic line`
- **WHEN** the text or JSON formatter renders the record
- **THEN** the token value is replaced with `[REDACTED]`
- **AND** `safe diagnostic line` remains

#### Scenario: Bearer glued colon tail is redacted

- **GIVEN** a WARNING or higher record contains
  `Bearer abc.def:GLUEDTAIL, status=502`
- **WHEN** the text or JSON formatter renders the record
- **THEN** the rendered text contains `Bearer [REDACTED], status=502`
- **AND** neither `abc.def` nor `GLUEDTAIL` appears

#### Scenario: Same-line authorization truncation is unchanged

- **GIVEN** a WARNING or higher record contains
  `Authorization: Basic dXNlcjpwYXNz status=failed` on one line with no comma
- **WHEN** the text formatter renders the record
- **THEN** the credential is redacted
- **AND** `status=failed` is not present on that line

#### Scenario: Line terminators are preserved and redaction is idempotent

- **GIVEN** rendered secret-bearing text that uses LF and CRLF separators
- **WHEN** secret-pattern redaction is applied once and then again
- **THEN** the terminator bytes and line count are unchanged
- **AND** the second pass equals the first

#### Scenario: Malformed proxy authorization scheme fails closed

- **WHEN** a WARNING or higher log contains an explicit Proxy-Authorization field with a malformed Bearer-like scheme and a credential parameter list
- **THEN** the entire unquoted field value is redacted through the current line
- **AND** no credential parameters survive in text or JSON output
- **AND** the following diagnostic line is preserved

### Requirement: Explicit authorization fields are masked without credential-boundary guesses

At WARNING or higher, an explicit case-insensitive `authorization` or `proxy-authorization` field in rendered text or an error-log field MUST have its complete value masked. A complete single- or double-quoted value MUST retain its field delimiters and adjacent context. An unquoted or unterminated value MUST be masked through the current line end, including comma or ampersand separated parameters, diagnostic-looking keys, malformed parameters, whitespace-separated tails and tails following a redaction placeholder. A placeholder MUST NOT establish that a field is safe. In multiline rendered logs, CR and LF delimiters and subsequent lines MUST remain intact; repeated redaction MUST produce identical output. Existing standalone Basic/Bearer token redaction and structured secret-key masking MUST remain intact.

#### Scenario: Quoted comma and malformed auth parameters cannot leave tails

- **WHEN** an authorization value contains quoted commas, repeated commas, malformed parameters or a parameter named status
- **THEN** no credential value reaches error fields, text/JSON log messages or rendered exceptions

#### Scenario: Quoted complete fields preserve context

- **WHEN** a Python-repr or JSON-style authorization field has a complete quoted value
- **THEN** the entire value is masked while its quotes and following field context remain

#### Scenario: Placeholder followed by credential material is not trusted

- **WHEN** an unquoted authorization field contains Bearer followed by a redaction placeholder and further material
- **THEN** all following material on that line is masked

#### Scenario: Following diagnostic lines and idempotency are retained

- **WHEN** an authorization field is followed by LF, CRLF or CR and a diagnostic line
- **THEN** those terminators and the next line survive unchanged
- **AND** applying the redactor again gives the same result

#### Scenario: Proxy header repr preserves the Basic scheme while masking tails

- **WHEN** a quoted Proxy-Authorization mapping field contains a Basic value, including a preexisting placeholder followed by credential material
- **THEN** the rendered value keeps its Basic scheme spelling with only the redaction placeholder
- **AND** credential tails do not survive repeated redaction

