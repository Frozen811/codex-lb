## MODIFIED Requirements

### Requirement: OpenAI-compatible image generation endpoint

The system SHALL expose `POST /v1/images/generations` and accept the OpenAI Images API request shape (`model`, `prompt`, `n`, `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, `partial_images`, `stream`, `user`). The endpoint MUST require `model` to start with `gpt-image-` and MUST treat `gpt-image-2` as the default if unspecified; the default is the fixed constant `DEFAULT_PUBLIC_IMAGE_MODEL` in `app/core/openai/images.py` and MUST NOT be operator-configurable. The endpoint MUST accept models in the `gpt-image-2` family, including `gpt-image-2`, `gpt-image-2.5-flare`, and `gpt-image-2.5-sunburst`, under the same parameter validation matrix. The endpoint MUST accept `background=transparent` with PNG or WebP output, MUST reject transparent JPEG before upstream dispatch with `param=output_format`, and MUST preserve upstream image bytes without post-processing. The endpoint MUST NOT expose the internal "host" Responses model used to invoke the built-in `image_generation` tool. The endpoint MUST accept `1 <= n <= 10` (`MAX_IMAGE_FANOUT`) for non-streaming requests, fanning out concurrent internal Responses calls and aggregating results. Streaming requests with `n > 1` MUST be rejected with HTTP 400.

#### Scenario: Compatible image generation request returns a JSON envelope

- **WHEN** a client sends `POST /v1/images/generations` with `model=gpt-image-2`, a non-empty `prompt`, and no `stream`
- **THEN** the service returns 200 with a JSON body of shape `{created, data: [{b64_json, revised_prompt}], usage}` containing exactly one entry

#### Scenario: Unsupported model is rejected

- **WHEN** a client sends `POST /v1/images/generations` with `model` not starting with `gpt-image-`
- **THEN** the service returns 400 with OpenAI `invalid_request_error` and `param: model`

#### Scenario: Per-model parameter rules are enforced for gpt-image-2 family

- **WHEN** a client sends `gpt-image-2`, `gpt-image-2.5-flare`, or `gpt-image-2.5-sunburst` with `input_fidelity=low|high`, or with `size` violating the gpt-image-2 size constraints (max edge ≤ 3840 px, both edges multiples of 16, ratio ≤ 3:1, total pixels in [655_360, 8_294_400])
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

#### Scenario: Transparent PNG or WebP generation and editing

- **WHEN** a client requests transparent PNG or WebP output through a supported generation or edit route, with JSON or streaming output
- **THEN** the image tool receives the requested background and format unchanged and returned image bytes remain unchanged

#### Scenario: Transparent JPEG is refused before dispatch

- **WHEN** a client requests transparent JPEG output through generation or editing
- **THEN** the service returns HTTP 400 with OpenAI invalid_request_error and param=output_format without calling upstream

### Requirement: Image generation streaming uses canonical OpenAI Images events

When a client requests `stream=true` on `/v1/images/generations` or `/v1/images/edits`, the system SHALL translate upstream Responses SSE events into the OpenAI Images streaming format. Generation requests MUST use `image_generation.*` event names, and edit requests MUST use `image_edit.*` event names. The system MUST emit the corresponding `partial_image` event for each upstream `response.image_generation_call.partial_image` and the corresponding `completed` event for *every* `image_generation_call` ResponseItem the upstream surfaces, in arrival order, when the trailing `response.completed` arrives. The `usage` field MUST be attached only to the final `completed` event so multi-image responses match the OpenAI Images streaming shape. The system MUST NOT forward Responses-specific events (`response.created`, `response.in_progress`, `response.image_generation_call.in_progress`, `response.image_generation_call.generating`, reasoning/content events) to the client. The system MUST also surface upstream errors that occur before the first SSE chunk as a structured OpenAI error envelope rather than a broken/truncated stream body.

#### Scenario: Partial images are forwarded with stable field names

- **WHEN** the upstream stream emits `response.image_generation_call.partial_image` with `partial_image_b64` and `partial_image_index`
- **THEN** the client receives `image_generation.partial_image` for generation or `image_edit.partial_image` for editing with `b64_json` set to `partial_image_b64`, the same `partial_image_index`, and the upstream `size`, `quality`, `background`, and `output_format`

#### Scenario: Final image completes the stream

- **WHEN** the upstream stream emits `response.output_item.done` with `item.type == "image_generation_call"` and a non-empty `result`
- **THEN** the client receives `image_generation.completed` for generation or `image_edit.completed` for editing with `b64_json`, `revised_prompt`, `size`, `quality`, `background`, and `output_format`, followed by a terminating `[DONE]`-equivalent event

#### Scenario: Upstream image generation failure becomes a single error event

- **WHEN** the upstream stream surfaces `response.failed` or an `image_generation_call` with `status == "failed"`
- **THEN** the client receives a single `error` event using an OpenAI error envelope and the SSE stream is closed cleanly
