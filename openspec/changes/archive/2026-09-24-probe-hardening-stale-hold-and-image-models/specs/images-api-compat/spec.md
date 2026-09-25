### Requirement: OpenAI-compatible image generation endpoint

The system SHALL expose `POST /v1/images/generations` and accept the OpenAI Images API request shape (`model`, `prompt`, `n`, `size`, `quality`, `background`, `output_format`, `output_compression`, `moderation`, `partial_images`, `stream`, `user`). The endpoint MUST require `model` to start with `gpt-image-` and MUST treat `gpt-image-2` as the default if unspecified; the default is the fixed constant `DEFAULT_PUBLIC_IMAGE_MODEL` in `app/core/openai/images.py` and MUST NOT be operator-configurable. The endpoint MUST accept models in the `gpt-image-2` family, including `gpt-image-2`, `gpt-image-2.5-flare`, and `gpt-image-2.5-sunburst`, under the same parameter validation matrix. The endpoint MUST NOT expose the internal "host" Responses model used to invoke the built-in `image_generation` tool.

#### Scenario: Per-model parameter rules are enforced for gpt-image-2 family
- **WHEN** a client sends `gpt-image-2`, `gpt-image-2.5-flare`, or `gpt-image-2.5-sunburst` with `background=transparent` or `input_fidelity=low|high`, or with `size` violating the gpt-image-2 size constraints (max edge ≤ 3840 px, both edges multiples of 16, ratio ≤ 3:1, total pixels in [655_360, 8_294_400])
- **THEN** the service returns 400 with OpenAI `invalid_request_error` describing the rejected parameter

#### Scenario: Compatible GPT Image 2.5 generations request succeeds
- **WHEN** a client sends `POST /v1/images/generations` with `model=gpt-image-2.5-flare` or `model=gpt-image-2.5-sunburst` and a valid prompt
- **THEN** the request passes validation and the chosen model is preserved in the upstream `image_generation` tool configuration
