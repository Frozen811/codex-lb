## ADDED Requirements

### Requirement: Plain warmup fallback requires upstream completion

After an upstream compact warmup HTTP 404, the system MUST send at most one plain Responses fallback pinned to the same account with stream enabled, storage disabled, and unsupported output-limit fields omitted. The system MUST report success only after receiving response.completed and MUST preserve upstream usage when supplied without inventing token counts when usage is absent.

#### Scenario: Compatible fallback completes
- **WHEN** compact warmup returns HTTP 404 and the plain fallback receives response.completed
- **THEN** warmup reports the selected account as submitted and records the upstream usage, or absent usage when not supplied

#### Scenario: Fallback ends without completion
- **WHEN** compact warmup returns HTTP 404 and the plain fallback ends without response.completed
- **THEN** warmup reports failure and MUST NOT record successful warmup or invented usage

#### Scenario: Other compact errors do not fall back
- **WHEN** compact warmup returns an upstream HTTP error other than 404
- **THEN** warmup MUST NOT submit a plain fallback
