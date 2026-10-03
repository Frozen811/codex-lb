## ADDED Requirements

### Requirement: Source base instructions are preserved in Codex catalogs

For an enabled Responses-capable model source, `GET /backend-api/codex/models`
and the Codex catalog view of `GET /v1/models?client_version=...` MUST report
string-valued `base_instructions` from its stored model metadata unchanged,
including whitespace and Unicode. Missing or non-string values MUST report
an empty string. Updating source metadata MUST affect the next catalog read
without a restart and MUST preserve unrelated capability metadata. Server-side
request overrides and source credentials MUST NOT appear in catalog entries.

#### Scenario: Stored instructions retain exact content after an update

- **WHEN** an operator stores and then updates string-valued source instructions containing whitespace and Unicode
- **THEN** both Codex catalog views return the latest exact string
- **AND** the source's other declared capabilities remain available

#### Scenario: Missing or malformed instructions retain the empty default

- **WHEN** stored source instructions are absent, null or a non-string JSON value
- **THEN** both Codex catalog views return an empty string
- **AND** neither server-side overrides nor source credentials appear in the catalog

### Requirement: Compatible output budgets use valid upstream counts

OpenAI-compatible model entries in `GET /v1/models`, individual model retrieval
and the `data` alias of `GET /backend-api/codex/models` MUST prefer a positive
non-boolean integer upstream `max_output_tokens`. If no such count exists,
`gpt-6-astra`, `gpt-6-sol` and `gpt-6-luna` MUST report the existing compatibility
fallback of 128000. Booleans, zero, negatives, strings and floats MUST NOT
override known compatibility fallbacks; a model with no valid count or known
fallback MUST report null. `metadata.max_output_tokens`,
`capabilities.max_output_tokens`, `max_output_tokens` and `maxOutputTokens`
MUST agree. Resolving an output budget MUST NOT alter input context budgets,
raw registry metadata or native Codex catalog entries.

#### Scenario: GPT-6 missing or malformed output budgets use the fallback

- **WHEN** a GPT-6 Astra, Sol or Luna entry has no positive non-boolean integer upstream output budget
- **THEN** all compatible output-budget fields report 128000 on list, retrieval and data-alias surfaces
- **AND** its input context budget and native metadata remain unchanged

#### Scenario: Valid upstream budget wins even when smaller than the fallback

- **WHEN** a GPT-6 model has upstream `max_output_tokens=96000`
- **THEN** every compatible output-budget field reports 96000

#### Scenario: Unknown model does not invent an output budget

- **WHEN** a model without a known fallback supplies an invalid output budget
- **THEN** compatible output-budget fields report null
