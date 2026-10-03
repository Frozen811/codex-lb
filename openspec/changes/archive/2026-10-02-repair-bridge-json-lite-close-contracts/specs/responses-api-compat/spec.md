## ADDED Requirements

### Requirement: HTTP bridge preserves complete WebSocket JSON documents

The HTTP bridge MUST parse each upstream text message as one complete JSON document regardless of indentation, LF, CRLF or surrounding JSON whitespace. Interpreted native payloads and parsed text MUST have equivalent event semantics. All relayed JSON events MUST use valid SSE framing that preserves their complete payload, including tool items and escaped newlines in strings.

#### Scenario: Formatted upstream error is terminal

- **WHEN** upstream sends a compact, indented or CRLF-formatted invalid_request_error before response creation
- **THEN** the client receives the actual code, type and parameter without an eventless timeout or identical replay
- **AND** a following valid request can complete on the same account

#### Scenario: Formatted lifecycle and tool items survive

- **WHEN** upstream emits formatted response.created, output_item.done and response.completed documents
- **THEN** each delivered SSE payload is complete JSON with its original content and the turn settles normally

### Requirement: Responses Lite signals serialize tool calls

Every final upstream Responses payload advertised as Lite by the trusted canonical HTTP header or WebSocket marker MUST set parallel_tool_calls to false, whether the client omitted it, supplied null, true or false. This normalization MUST preserve input, tools, cache identity and unrelated reasoning members. It MUST NOT establish Lite trust from arbitrary inbound headers or metadata. Non-Lite payloads MUST retain their existing transport-specific serialization policy.

#### Scenario: Lite bridge request reaches upstream serialized

- **WHEN** a body-derived Lite request reaches the upstream WebSocket through a public HTTP route
- **THEN** the outgoing body contains parallel_tool_calls=false and reasoning.context=all_turns with the original input and cache identity

#### Scenario: Lite direct HTTP and fallback agree

- **WHEN** a body-derived Lite request uses direct HTTP or WebSocket-to-HTTP fallback
- **THEN** the final HTTP payload contains parallel_tool_calls=false and the canonical Lite HTTP header

#### Scenario: Untrusted marker remains non-Lite

- **WHEN** a non-Lite client supplies a Lite header or marker without trusted continuity
- **THEN** it does not acquire Lite classification or Lite-specific normalization

## MODIFIED Requirements

### Requirement: WebSocket close 1009 is terminal and account-neutral

When an upstream adapter exposes close code 1009 for pending Responses work,
the HTTP bridge and direct WebSocket relay MUST report payload_too_large.
This is an exact-code exception to "Upstream websocket drops penalize affected
accounts": it MUST NOT cause identical replay, account exclusion/rotation or
account error-health writes. Existing terminal cleanup MUST settle reservations,
release response-create ownership and retire the failed socket.

Before an HTTP response is committed the error MUST use HTTP 400 with
type=invalid_request_error and param=input. After commitment it MUST use the
existing terminal SSE error contract without duplicating visible output.
The direct WebSocket route MUST use its existing terminal error envelope.
Explicit request-state overrides MUST remain authoritative.

Typed WebSocket message-size errors with exact code 1009 MUST preserve the
same terminal size evidence even when the transport reports an error event
instead of a received close frame. Other protocol or transport errors MUST
retain their existing classification.

#### Scenario: Single account rejects the message size

- **WHEN** the only selected account closes 1009 before response.created
- **THEN** the client receives payload_too_large without another dispatch or a no_accounts replacement
- **AND** a following valid request can select that same account

#### Scenario: Close after output

- **WHEN** upstream closes 1009 after response creation or visible output
- **THEN** exactly one terminal size error is delivered without replaying the turn
- **AND** already-delivered output is not duplicated

#### Scenario: Other disconnects are unchanged

- **WHEN** the adapter exposes 1000, 1006, another close code, or no close code
- **THEN** this exception does not replace the existing retry and error classification

#### Scenario: Reader reports a typed size error

- **WHEN** the WebSocket reader reports an exact-code 1009 message-size exception
- **THEN** the client receives terminal payload_too_large without account penalty or identical replay
- **AND** reservations, pending requests and response-create ownership are released
