## MODIFIED Requirements

### Requirement: Warmup sends minimal upstream responses request
For each submitted account, the system SHALL send a minimal upstream Responses API request intended to warm transport/session/model path behavior. The model used SHALL be the configured warmup model unless the authenticated API key has `enforcedModel`, in which case that enforced model is used instead (consistent with normal request enforcement). `warmup_model` SHALL NOT be sent as an upstream field. The warmup request SHALL remain small and deterministic. Submissions SHALL run in parallel with a maximum concurrency of 5 accounts per warmup execution. When an initial compact-based warmup request returns HTTP 404 because compaction triggers are not supported by the upstream endpoint, the system SHALL transparently fall back to a minimal plain Responses API request.

#### Scenario: Warmup request uses enforced model precedence when present
- **WHEN** an authenticated API key has `enforcedModel` configured
- **THEN** warmup upstream requests use `enforcedModel` for model selection and do not include a `warmup_model` upstream field

#### Scenario: Warmup fan-out is concurrency bounded
- **WHEN** a warmup execution submits requests for more than five accounts
- **THEN** the service runs warmup submissions in parallel while ensuring no more than five account submissions are in flight at once

#### Scenario: Warmup falls back to plain responses when compact 404s
- **GIVEN** an active account submitted for warmup
- **AND** upstream responds 404 to a compact warmup request
- **WHEN** warmup request submission encounters HTTP 404 on the compact path
- **THEN** the system transparently falls back to a minimal plain Responses API request
- **AND** records the account warmup as successful when the plain request completes
