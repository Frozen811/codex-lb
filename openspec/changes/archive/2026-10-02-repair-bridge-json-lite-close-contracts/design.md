## Context

The existing multiline parser and Lite finalizer pass their focused tests. Output-item events are reserialized later in the bridge, so their initial fast-path exclusion is not itself a proven defect. aiohttp emits `WSMsgType.ERROR` with `WebSocketError.code == 1009` on an oversized message; the adapter currently drops that code.

## Goals / Non-Goals

Verify exactly UP-PR-2530/2531/2539 through route behavior, transport bytes and settlement. No transport-policy redesign, new settings or changes to unrelated registry items.

## Decisions

- Preserve size evidence only for the typed aiohttp WebSocketError with exact code 1009; do not infer it from exception messages or generic code attributes. Other failures retain existing classification.
- Return the existing close message shape for this terminal size error before generic network classification. Existing bridge/direct relay logic then owns finalization and account-neutral behavior.
- Use existing route fixtures for the broad matrix and a local aiohttp WebSocket server for adapter-boundary proof. The test server supplies synthetic traffic; no external account credentials are needed.
- Document the already-implemented complete-document parsing and Lite parallel-call requirements explicitly, without changing signal trust.

## Risks / Trade-offs

Socket tests add asynchronous lifecycle responsibilities; close the client and server in finally blocks. Synthetic upstream coverage establishes local behavior, not cloud artifacts or real OpenAI traffic. The local size limit and an upstream received 1009 both identify a size error; neither justifies replay of the identical request.
