## ADDED Requirements

### Requirement: Unary Codex control requests preserve a single media type

Unary Codex control requests MUST forward at most one case-insensitive `Content-Type` field. Nonempty bodies MUST retain the inbound media type, including JSON and SDP. For native callers the first retained field spelling and position MUST be preserved. Requests with an absent or zero-byte body MUST omit `Content-Type` and MUST NOT cause the upstream transport to generate one. These rules MUST apply to direct and routed transports without changing payload bytes, query parameters or account identity.

#### Scenario: Nonempty control body preserves its media type

- **WHEN** a control request carries nonempty JSON or SDP with any casing of the media-type header
- **THEN** exactly one upstream media-type field retains its value and the body remains byte-identical
- **AND** a native caller retains the first field's spelling and position

#### Scenario: Empty POST and GET omit media type

- **WHEN** a control request carries no payload or a zero-byte POST payload
- **THEN** no upstream `Content-Type` field is sent, including a transport-generated field

## MODIFIED Requirements

### Requirement: Responses input images bypass the HTTP bridge

For `/v1/responses` and `/backend-api/codex/responses`, bounded inline images MUST reuse the HTTP responses bridge when inline-image admission is enabled, no `image_generation` tool is declared, and every input image anywhere in the input has a strict nonempty base64 PNG/JPEG data URL decoding to at most 5,000,000 bytes. Admitted image bytes MUST remain verbatim, including replayed history, and the existing thread connection and prompt-cache identity MUST be retained. A shape-valid image above the decoded limit or an admitted final frame above 64 MiB MUST fail locally with HTTP 400 `payload_too_large`, `param=input`, before dispatch, without slimming or a size-driven raw fallback. Explicit upstream HTTP policy and recent WebSocket failure fallback MUST retain their existing behavior.

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
