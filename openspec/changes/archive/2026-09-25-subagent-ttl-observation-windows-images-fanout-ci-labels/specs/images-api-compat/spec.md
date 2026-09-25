# images-api-compat Specification Delta

## MODIFIED Requirements

### Requirement: OpenAI-compatible image generation endpoint

The system SHALL expose `POST /v1/images/generations` and accept the OpenAI Images API request shape (`model`, `prompt`, `n`, `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, `partial_images`, `stream`, `user`). The endpoint MUST require `model` to start with `gpt-image-` and MUST treat `gpt-image-2` as the default if unspecified; the default is the fixed constant `DEFAULT_PUBLIC_IMAGE_MODEL` in `app/core/openai/images.py` and MUST NOT be operator-configurable. The endpoint MUST accept models in the `gpt-image-2` family, including `gpt-image-2`, `gpt-image-2.5-flare`, and `gpt-image-2.5-sunburst`, under the same parameter validation matrix. The endpoint MUST NOT expose the internal "host" Responses model used to invoke the built-in `image_generation` tool. The endpoint MUST accept `1 <= n <= 10` (`MAX_IMAGE_FANOUT`) for non-streaming requests, fanning out concurrent internal Responses calls and aggregating results. Streaming requests with `n > 1` MUST be rejected with HTTP 400.

#### Scenario: Compatible image generation request returns a JSON envelope

- **WHEN** a client sends `POST /v1/images/generations` with `model=gpt-image-2`, a non-empty `prompt`, and no `stream`
- **THEN** the service returns 200 with a JSON body of shape `{created, data: [{b64_json, revised_prompt}], usage}` containing exactly one entry

#### Scenario: Unsupported model is rejected

- **WHEN** a client sends `POST /v1/images/generations` with `model` not starting with `gpt-image-`
- **THEN** the service returns 400 with OpenAI `invalid_request_error` and `param: model`

#### Scenario: Per-model parameter rules are enforced for gpt-image-2 family

- **WHEN** a client sends `gpt-image-2`, `gpt-image-2.5-flare`, or `gpt-image-2.5-sunburst` with `background=transparent` or `input_fidelity=low|high`, or with `size` violating the gpt-image-2 size constraints (max edge ≤ 3840 px, both edges multiples of 16, ratio ≤ 3:1, total pixels in [655_360, 8_294_400])
- **THEN** the service returns 400 with OpenAI `invalid_request_error` describing the rejected parameter

#### Scenario: Compatible GPT Image 2.5 generations request succeeds

- **WHEN** a client sends `POST /v1/images/generations` with `model=gpt-image-2.5-flare` or `model=gpt-image-2.5-sunburst` and a valid prompt
- **THEN** the request passes validation and the chosen model is preserved in the upstream `image_generation` tool configuration

#### Scenario: Per-model parameter rules are enforced for legacy gpt-image models

- **WHEN** a client sends `gpt-image-1.5`, `gpt-image-1`, or `gpt-image-1-mini` with `size` outside `{1024x1024, 1536x1024, 1024x1536, auto}`
- **THEN** the service returns 400 with OpenAI `invalid_request_error` and `param: size`

#### Scenario: Multi-image requests are rejected until upstream support arrives

- **WHEN** a client sends `/v1/images/generations` or `/v1/images/edits` with `n > 10` or `n < 1`
- **THEN** the service returns 400 with OpenAI `invalid_request_error` and `param: n`
- **AND** a streaming request with `n > 1` returns 400 with OpenAI `invalid_request_error` and `param: n`

#### Scenario: Missing model defaults to images_default_model

- **WHEN** a client sends `/v1/images/generations` or `/v1/images/edits` without `model`
- **THEN** the service uses `gpt-image-2` as the publicly-effective model for validation, request log accounting, and the internal `image_generation` tool config
- **AND** a `CODEX_LB_IMAGES_DEFAULT_MODEL` value in the environment does not change that default (startup logs the removed-setting warning once)
