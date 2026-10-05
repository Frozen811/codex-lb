## ADDED Requirements

### Requirement: Supported image models in key model selection
The authenticated dashboard model catalog MUST expose every supported Images adapter model exactly once, including when the Responses catalog is empty. Image entries MUST carry `imageOnly: true`, no reasoning options and `sourceOnly: false`. Built-in image identifiers MUST win collisions with catalog or source models. Existing public/source model metadata and dashboard-read permissions MUST remain compatible. Create and edit allowlists MUST persist selected image identifiers. The public Responses model catalog MUST NOT gain adapter image entries, and Automations MUST exclude image-only entries from runnable model choices.

#### Scenario: Empty Responses catalog and collision
- **WHEN** the Responses catalog is empty or a source uses a supported image identifier
- **THEN** the dashboard still offers all supported images exactly once with image-only metadata

#### Scenario: Image allowlist roundtrip
- **WHEN** an administrator selects an image model while creating or editing a key
- **THEN** the saved allowlist contains that image model identifier
- **AND** Automations do not offer that identifier as a text generation model

#### Scenario: Permissions and public catalog
- **WHEN** a caller lacks dashboard-read permission or reads the public Responses catalog
- **THEN** existing permission refusal applies or the public catalog retains its text model contract respectively

## MODIFIED Requirements

### Requirement: Public OpenAI-compatible model list filtering

OpenAI-compatible model list endpoints SHALL filter native upstream entries using a single predicate that requires both conditions:
1. `model.supported_in_api` is true
2. If `allowed_models` is configured, the model is in the allowed set

This predicate SHALL be applied consistently to native upstream entries across `/api/models`, `/v1/models`, and the OpenAI-style `data` alias in `/backend-api/codex/models`. The dashboard catalog SHALL additionally expose supported Images adapter entries under the image model selection requirement and enabled source entries under their existing metadata contract; these additions MUST NOT expand the public native Responses catalog. The Codex-native `models` catalog in `/backend-api/codex/models` SHALL also expose unsupported upstream models only when the model is a Codex shell-command model (`shell_type="shell_command"`); unsupported non-shell models SHALL remain hidden.

#### Scenario: Unsupported model excluded from /v1/models

- **WHEN** a model snapshot contains a model with `supported_in_api=false`
- **THEN** that model is not included in the `/v1/models` response

#### Scenario: Unsupported non-shell model excluded from /backend-api/codex/models

- **WHEN** a model snapshot contains a model with `supported_in_api=false`
- **AND** the model is not a Codex shell-command model
- **THEN** that model is not included in the `/backend-api/codex/models` response

#### Scenario: Unsupported Codex shell model included only in Codex-native catalog

- **WHEN** a model snapshot contains a model with `supported_in_api=false`
- **AND** the model has `shell_type="shell_command"`
- **THEN** that model is included in `/backend-api/codex/models.models`
- **AND** that model is not included in `/backend-api/codex/models.data`
- **AND** its native entry is not included in `/api/models` or `/v1/models`

#### Scenario: Allowed but unsupported model excluded

- **WHEN** a model is in the `allowed_models` set but has `supported_in_api=false`
- **AND** the model is not a Codex shell-command model
- **THEN** that native model entry is not exposed in any model list endpoint

#### Scenario: gpt-5.3-codex aliases share availability gate consistently

- **WHEN** `gpt-5.3-codex` has `supported_in_api=false`
- **AND** `gpt-5.3-codex-spark` has `supported_in_api=true`
- **THEN** `/api/models`, `/v1/models`, and `/backend-api/codex/models.data`
      expose `gpt-5.3-codex-spark` but do not expose `gpt-5.3-codex`

#### Scenario: Consistent model set across endpoints

- **WHEN** the same native registry is read through each catalog endpoint
- **THEN** `/api/models`, `/v1/models`, and `/backend-api/codex/models.data` expose the same filtered native upstream model set
- **AND** the dashboard additionally exposes supported Images adapters and enabled source models
