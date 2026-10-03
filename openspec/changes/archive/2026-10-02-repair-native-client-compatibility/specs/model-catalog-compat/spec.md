## ADDED Requirements

### Requirement: Individual model retrieval matches the visible catalog

`GET /v1/models/{model_id}` MUST return the same model fields as the matching visible `/v1/models` catalog entry, apart from independently generated creation timestamps. It MUST apply the same proxy authentication, model allowlist and source assignment scope. Missing or hidden models MUST return HTTP 404 with an OpenAI error envelope whose code is `model_not_found` and param is `model`. A trailing slash delimiter MUST be accepted directly without changing the model identifier; identifiers containing internal slashes MUST remain intact.

#### Scenario: Retrieve a visible nested model ID with a trailing slash
- **WHEN** a client retrieves a visible model whose ID contains an internal slash, with or without the final slash delimiter
- **THEN** both requests return the matching catalog model object directly with HTTP 200

#### Scenario: Excluded or missing models fail closed
- **WHEN** a client retrieves an unknown model or a model excluded by its allowlist or source scope
- **THEN** the proxy returns HTTP 404 `model_not_found`
- **AND** hidden model metadata is not exposed
