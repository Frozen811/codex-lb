## Scope and decisions

This batch verifies UP-PR-2530, UP-PR-2531 and UP-PR-2539. Whole-document WebSocket parsing and Lite normalization already exist. The aiohttp size-error boundary needs a narrow repair: typed WebSocketError(1009) becomes existing close evidence before generic transport recovery.

## Failure modes and example

A local WebSocket reader exceeding its message limit emits ERROR(WebSocketError(1009)), not a received CLOSE frame. Previously that became an unclassified disconnect and could rotate or penalize the account. It should follow the same terminal cleanup as received close 1009. For example, an oversized response before response.created produces payload_too_large, and a following small request can select the same account.

Pretty JSON with CRLF remains one WebSocket document and is framed as valid SSE. Lite classification from an additional_tools prefix forces parallel_tool_calls=false while preserving the input/tools; an untrusted inbound marker does not enable Lite.

## Verification boundary

Local routes, isolated SQLite reservations and loopback WebSocket traffic only. Published images, cloud CI, deployed replicas and real client/account traffic remain separate.
