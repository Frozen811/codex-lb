## MODIFIED Requirements

### Requirement: Image generation is implemented as a Responses tool adapter

The system SHALL implement `/v1/images/generations` and `/v1/images/edits` by issuing an internal `/v1/responses` request whose `tools` array includes `{"type": "image_generation", ...}`. The internal request MUST use dedicated ordered Images host selection that prefers visible, unsuppressed `gpt-5.6-sol`, then `gpt-6-astra`, then `gpt-5.5`. Images selection MUST NOT choose `gpt-5.6-luna` and MUST default to `gpt-5.6-sol` when no compatible candidate is visible. Selection MUST remain independent from the default account-probe host selection. The public `gpt-image-*` model MUST remain in the image tool configuration and MUST NOT be replaced by the internal host model. The system MUST route that internal request through the existing proxy account-selection, sticky session, retry, and authentication pipeline. The system MUST NOT introduce a new `chatgpt-token → openai-api-key` token-exchange path solely to support these endpoints.

#### Scenario: Images routes prefer an image-compatible host

- **GIVEN** `gpt-5.6-sol` is visible and unsuppressed in the model registry
- **WHEN** a client sends a valid generation or edit request
- **THEN** the internal Responses request uses `gpt-5.6-sol` as its host model
- **AND** the image tool retains the publicly requested `gpt-image-*` model

#### Scenario: Images fallback excludes Luna

- **GIVEN** Sol and Astra are unavailable or suppressed, and Luna and 5.5 are visible
- **WHEN** a generation or edit request selects its internal host
- **THEN** it uses `gpt-5.5` rather than Luna
- **AND** when only Luna is visible it uses the existing Sol default

#### Scenario: Images host selection does not change account probes

- **WHEN** Images host preference changes
- **THEN** the default account-probe host order remains unchanged

#### Scenario: Internal Responses call uses existing routing

- **WHEN** any `/v1/images/*` request is processed
- **THEN** account selection, sticky-session affinity, API-key validation, and request budgeting use the same code paths as `/v1/responses`

#### Scenario: Multipart edits become input_image content

- **WHEN** an edit request includes `image` and optional `mask` multipart parts
- **THEN** each binary part is encoded as a `data:` URL and inserted as `input_image` content in the internal Responses input
