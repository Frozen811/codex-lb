## MODIFIED Requirements

### Requirement: Responses input images bypass the HTTP bridge

For `/v1/responses` and `/backend-api/codex/responses`, bounded inline images MUST reuse the HTTP responses bridge when inline-image admission is enabled, no `image_generation` tool is declared, and every input image anywhere in the input has a strict nonempty base64 PNG/JPEG data URL decoding to at most 5,000,000 bytes. Admitted image bytes MUST remain verbatim, including replayed history, and the existing thread connection and prompt-cache identity MUST be retained. A shape-valid image above the decoded limit or an admitted final frame above 64 MiB MUST fail locally with HTTP 400 `payload_too_large`, `param=input`, before dispatch, without slimming or a size-driven raw fallback. Malformed base64 MUST remain an unsupported shape even above the encoded length shortcut, and MUST take precedence over a valid oversized sibling anywhere in the input. Explicit upstream HTTP policy and recent WebSocket failure fallback MUST retain their existing behavior.

Other image-bearing requests, including compact requests, MUST retain their existing raw-path routing or uploaded-reference rejection. Disabling inline-image admission MUST restore the blanket image bypass. A raw image bypass MUST be request-local and MUST NOT by itself pin upstream HTTP. Image creates without acknowledgement MUST retain the existing bounded pre-created retry policy and original request deadline; an exhausted deadline MUST NOT permit another dispatch. Their terminal path MUST release pending admission and settle the reservation. A terminal invalid-image error MUST be surfaced promptly without replay and MUST leave subsequent text turns usable.

#### Scenario: Nested input_image bypasses bridge

- **GIVEN** the HTTP responses bridge is enabled
- **WHEN** a request contains an input image that fails bounded inline admission
- **THEN** it uses the existing raw-path routing or uploaded-reference rejection

#### Scenario: Image bypass does not disable future text bridge use

- **GIVEN** the HTTP responses bridge is enabled
- **WHEN** an image-bearing request bypasses the bridge
- **THEN** the bypass applies only to that request
- **AND** a later text-only request can still use the HTTP responses bridge

#### Scenario: Image bypass does not pin the upstream transport

- **GIVEN** the HTTP responses bridge is enabled and upstream transport is auto
- **WHEN** an image request below the WebSocket frame budget bypasses the bridge
- **THEN** ordinary upstream transport policy decides the transport without an image-driven HTTP pin

#### Scenario: Text image text retains the same connection

- **WHEN** a thread sends text, an admitted inline image, then text with replayed image history
- **THEN** all turns use the existing bridge socket and preserve image bytes and prompt-cache identity

#### Scenario: Unacknowledged image cannot outlive its request budget

- **WHEN** an admitted image create is dispatched and upstream returns no acknowledgement before the request budget is exhausted
- **THEN** it terminates without another dispatch beyond the original budget
- **AND** its reservation and pending admission settle

#### Scenario: Invalid image does not poison the next text turn

- **WHEN** upstream rejects an admitted image before response creation
- **THEN** the client receives the terminal image error
- **AND** a subsequent text turn can complete on the same account

#### Scenario: Malformed oversized base64 retains unsupported-shape precedence

- **WHEN** an input image has malformed base64 above the encoded length shortcut, including alongside a valid oversized image
- **THEN** the request retains unsupported-image raw-path routing without a bridge-generated payload_too_large error
- **AND** a legal oversized image without an unsupported sibling still fails before dispatch

### Requirement: A disabled model source refuses its models instead of falling through

The system SHALL NOT dispatch to a subscription account a request whose model
is served by an OpenAI-compatible model source that an operator has switched
off. It SHALL refuse such a request with HTTP status `503` and error code
`model_source_disabled`.

"Switched off" covers both a disabled source row and a disabled model row on an
enabled source. The refusal SHALL apply on `/v1/chat/completions`,
`/v1/responses`, and `/backend-api/codex/responses`.

The refusal SHALL be decided by the ordinary source-selection rules with the
enabled-state filter inverted and nothing else changed: same candidate list
(raw client alias and normalized model), same API key model allowlist, same
source assignment scope, same subscription-registry precedence, same route
shape, same streaming requirement. A request that the ordinary lookup would
have missed for any reason other than enabled state MUST keep its existing
behaviour, including a model no source exposes, a source the API key is not
assigned to, a chat-only source asked for a Responses route, and a
subscription-registry slug that an unscoped API key never source-routes.

Responses requests without a terminal Codex compaction trigger that are pinned
to the subscription account that received an uploaded file MUST NOT be refused by disabled-source lookup and MUST proceed to
subscription routing as before. Terminal Codex compaction triggers MUST follow
the source-owned remote-compaction refusal contract before native admission.

The WebSocket transport cannot forward to a model source, so its
source-ownership guards SHALL treat a model owned only by a switched-off source
as source-owned: the turn fails with the existing service-level
`model_source_requires_http_transport` refusal instead of dispatching to a
subscription account, and the client's HTTP fallback then meets the
`model_source_disabled` refusal above. The guards' existing exclusions — a
structurally excluded request and a recorded previous-response subscription
owner — keep bypassing the guard unchanged.

The refusal MUST happen before any usage reservation is taken, so a refused
request strands no reservation, and MUST NOT create a request log entry for a
dispatch that never happened.

#### Scenario: Chat request for a disabled source's model is refused

- **GIVEN** an OpenAI-compatible model source exposes model `m` and is disabled
- **WHEN** a client calls `POST /v1/chat/completions` with model `m`
- **THEN** the response is `503` with error code `model_source_disabled`
- **AND** no subscription account is selected for the request
- **AND** no usage reservation is left held

#### Scenario: Responses request for a disabled source's model is refused

- **GIVEN** a Responses-capable OpenAI-compatible model source exposes model `m` and is disabled
- **WHEN** a client calls `POST /v1/responses` or `POST /backend-api/codex/responses` with model `m`
- **THEN** the response is `503` with error code `model_source_disabled`
- **AND** no subscription account is selected for the request

#### Scenario: A disabled model on an enabled source is refused

- **GIVEN** an enabled OpenAI-compatible model source whose model row for `m` is disabled
- **WHEN** a client calls `POST /v1/chat/completions` with model `m`
- **THEN** the response is `503` with error code `model_source_disabled`

#### Scenario: A model no source exposes is unaffected

- **GIVEN** no model source exposes model `m`, enabled or disabled
- **WHEN** a client calls `POST /v1/chat/completions` with model `m`
- **THEN** subscription routing proceeds exactly as it did before this requirement

#### Scenario: A WebSocket turn for a disabled source's model bounces to HTTP

- **GIVEN** a Responses-capable OpenAI-compatible model source exposes model `m` and is disabled
- **WHEN** a client requests model `m` over the WebSocket transport, at connect time or on a later turn over an already-open socket
- **THEN** the turn is refused with the service-level `model_source_requires_http_transport` failure that makes Codex clients retry over the HTTP transport
- **AND** the turn is not forwarded to a subscription account upstream

#### Scenario: A subscription slug shadowed by a disabled source is unaffected

- **GIVEN** a disabled OpenAI-compatible model source lists a slug the subscription model registry already serves
- **AND** an API key without source assignment scoping
- **WHEN** the key requests that slug
- **THEN** the request is not refused with `model_source_disabled`
- **AND** subscription routing proceeds unchanged

### Requirement: Request logs expose upstream Responses transport
For streaming Responses proxy requests, persisted request logs MUST distinguish the downstream client transport from the upstream egress transport by recording the upstream transport in `request_logs.upstream_transport` while preserving `request_logs.transport` as the downstream client transport. New attempts MUST record the resolved `http` or `websocket` egress rather than the configured `auto` mode, while retaining that mode for client-side transport fallback.

#### Scenario: downstream HTTP single-shot records upstream HTTP
- **GIVEN** the downstream request transport is HTTP
- **AND** smart HTTP-downstream routing chooses upstream HTTP for a single-shot Responses request
- **WHEN** the request log is persisted
- **THEN** `transport` is `"http"`
- **AND** `upstream_transport` is `"http"`

#### Scenario: downstream HTTP sticky records preserved auto upstream mode
- **GIVEN** the downstream request transport is HTTP
- **AND** smart HTTP-downstream routing keeps the base upstream `"auto"` mode for a sticky Responses request
- **WHEN** the request log is persisted
- **THEN** `transport` is `"http"`
- **AND** `upstream_transport` is the resolved `"http"` or `"websocket"` egress

#### Scenario: historical or unrelated rows tolerate missing upstream transport
- **GIVEN** a request log row predates upstream transport persistence or belongs to a request kind that does not know its upstream transport
- **WHEN** the row is read
- **THEN** `upstream_transport` MAY be null
- **AND** the existing request-log response MUST remain valid

### Requirement: OpenAI-compatible sources route only compatible public routes

OpenAI-compatible model sources SHALL be eligible for public OpenAI-compatible
routes only when the source declares support for the route shape. Chat
Completions-compatible sources MAY serve `/v1/chat/completions`.
Responses-compatible sources MAY serve `/v1/responses` and
`/backend-api/codex/responses`. Audio-transcriptions-compatible sources MAY
serve `/v1/audio/transcriptions`. Codex-native compaction, file upload,
control-plane, and websocket bridge paths MUST remain subscription-backed unless
a later requirement explicitly defines OpenAI-compatible source behavior for
those paths.

#### Scenario: Chat completions routes to OpenAI-compatible source

- **GIVEN** an enabled OpenAI-compatible source declares chat-completions support
- **AND** the authenticated API key is allowed to use that source/model
- **WHEN** the client calls `POST /v1/chat/completions` with that model
- **THEN** the proxy forwards the request to the source's configured base URL
  using the source's upstream API key

#### Scenario: Codex-native Responses route uses Responses-compatible source

- **GIVEN** an enabled OpenAI-compatible source declares Responses support
- **AND** it exposes model `deepseek-v4-flash`
- **WHEN** a client calls `POST /backend-api/codex/responses` with model `deepseek-v4-flash`
- **THEN** the proxy forwards the request to that source's Responses endpoint

#### Scenario: Chat-only source is not used for Codex-native Responses route

- **GIVEN** an enabled OpenAI-compatible source exposes model `local-coder`
- **AND** the source declares Chat Completions support only
- **WHEN** a client calls `POST /backend-api/codex/responses` with model `local-coder`
- **THEN** the request is not routed to that source
- **AND** subscription-backed Codex routing rules continue to apply

#### Scenario: Compaction request is not source-routed

- **GIVEN** an enabled Responses-compatible source exposes model `deepseek-v4-flash`
- **AND** a client calls `POST /backend-api/codex/responses` for that model whose
  input contains a `compaction_trigger` item
- **THEN** the request is not forwarded to the external source
- **AND** it receives the source-owned remote-compaction refusal before subscription admission

#### Scenario: V1 compaction_trigger remains eligible for model sources

- **GIVEN** an enabled Responses-compatible source exposes model `deepseek-v4-flash`
- **AND** a client calls `POST /v1/responses` for that model whose input ends with
  a terminal `compaction_trigger` item
- **THEN** the request remains eligible for that Responses-compatible source
- **AND** it is not forced onto subscription account selection by the Codex-only
  compaction source-route exclusion

#### Scenario: File-referencing request is not source-routed

- **GIVEN** an enabled Responses-compatible source exposes model `deepseek-v4-flash`
- **AND** a client calls `/backend-api/codex/responses` or `/v1/responses` for that
  model whose input references an uploaded `input_file`/`input_image` `file_id`
- **THEN** the request is not forwarded to the external source
- **AND** it follows the subscription path so the account-scoped file pin is honored

#### Scenario: Audio transcription routes to OpenAI-compatible source

- **GIVEN** an enabled OpenAI-compatible source declares audio transcriptions support
- **AND** it exposes model `whisper-large-v3`
- **WHEN** the client calls `POST /v1/audio/transcriptions` with multipart
  field `model=whisper-large-v3`
- **THEN** the proxy forwards the multipart request to the source's
  `/audio/transcriptions` endpoint
- **AND** the request uses the source's upstream API key

#### Scenario: Non-source transcription model keeps subscription validation

- **GIVEN** no audio-transcriptions-compatible source exposes model `gpt-4o-mini`
- **WHEN** the client calls `POST /v1/audio/transcriptions` with
  `model=gpt-4o-mini`
- **THEN** the proxy returns the existing unsupported transcription model error

### Requirement: Codex compact requests are bounded by the proxy request budget
When `/backend-api/codex/responses/compact` is called for Codex auto-compaction, the service MUST bound the upstream compact call by the remaining proxy compact request budget. That budget (the dashboard `compact_request_budget_seconds`) is the only total cap on the upstream compact call; there is no separate upstream compact timeout setting. The service MUST preserve Codex turn metadata `request_kind` in compact request logs so auto-compaction failures are distinguishable from normal user turns.

#### Scenario: auto-compaction cannot hang past the proxy budget
- **GIVEN** a Codex compact request carries `x-codex-turn-metadata` with `request_kind: "compaction"`
- **WHEN** the service calls upstream
- **THEN** the upstream call receives both connect and total timeout overrides from the remaining compact request budget
- **AND** no other total timeout is applied to the upstream compact call
- **AND** the request log records `request_kind` as `compaction`

The default total compact budget MUST be 900 seconds. A remaining-budget override MUST only shorten the configured total budget. Without an override, SSE event collection MUST use the independent stream idle timeout; with an override, the collector MUST use that override while the configured total cap remains authoritative.

#### Scenario: Default compact budget preserves the long response window
- **WHEN** no compact budget is configured
- **THEN** the total budget is 900 seconds and the upstream call retains the existing settlement reserve

#### Scenario: An explicit budget and override cannot widen the total cap
- **WHEN** the configured compact budget is 60 seconds and a remaining-budget override is 120 seconds
- **THEN** the low-level total timeout remains at most 60 seconds

#### Scenario: SSE idle collection is independent without an override
- **WHEN** the total budget is 900 seconds and the stream idle timeout is 45 seconds without an override
- **THEN** the SSE collector uses 45 seconds while the total timeout retains the compact budget


## ADDED Requirements

### Requirement: Source-owned models refuse remote compaction before native admission

Terminal compaction triggers on `/backend-api/codex/responses` and explicit
`/backend-api/codex/responses/compact` and `/v1/responses/compact` requests MUST
refuse models owned by enabled Responses-compatible sources with HTTP 400,
`code=compaction_unsupported` and `type=invalid_request_error`. Models owned
only by a disabled source MUST receive HTTP 503 `model_source_disabled` with
`type=upstream_error`. Refusal MUST precede subscription selection, admission,
reservation and upstream dispatch, and MUST NOT create a dispatch request log.

Ownership MUST follow the existing source candidate order, model allowlist,
source-assignment scope and subscription-registry precedence. Source refusal
MUST NOT change ordinary source streaming or the existing `/v1/responses`
terminal-trigger forwarding semantics. The two explicit compact endpoints with
a trailing slash MUST execute the same validation, routing, ownership and
accounting behavior as their canonical forms, without requiring a redirect.

#### Scenario: Enabled source compact request is refused

- **WHEN** a source-owned model requests terminal Codex compaction or either explicit compact endpoint
- **THEN** it receives `400 compaction_unsupported` before selection, admission, reservation or dispatch
- **AND** no dispatch request log is created

#### Scenario: Disabled source compact request is refused

- **WHEN** only a disabled Responses-compatible source owns the compact model
- **THEN** the client receives `503 model_source_disabled` without native admission or dispatch

#### Scenario: Assigned API key limits remain untouched by refusal

- **WHEN** a key with a model allowlist, source assignment and token limit requests compaction for its assigned source model
- **THEN** the unsupported request leaves no reservation

#### Scenario: Trailing-slash source compaction uses the same refusal

- **WHEN** an enabled or disabled source model requests an explicit compact endpoint with a trailing slash
- **THEN** it receives the same refusal as the canonical endpoint without a redirect

#### Scenario: Trailing-slash native compaction preserves success

- **WHEN** a subscription model successfully compacts through either explicit endpoint with a trailing slash
- **THEN** the same handler returns the compact result and preserves the native credentials and headers
