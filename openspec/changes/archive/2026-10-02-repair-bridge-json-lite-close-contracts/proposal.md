## Why

UP-PR-2530, UP-PR-2531 and UP-PR-2539 remain unverified in the independent registry despite existing source fixes. Verify complete WebSocket JSON delivery, Lite payload normalization and exact size-error classification through public routes and transport adapters; repair any demonstrated gaps.

## What Changes

- Add route regressions for formatted lifecycle/tool events and upstream errors, including native interpreted frames.
- Verify Lite and non-Lite outgoing payloads across bridge and direct HTTP transport.
- Preserve aiohttp message-size error evidence at the adapter boundary, with terminal account-neutral handling and settlement.
- Synchronize normative requirements, context and exactly three registry entries with scoped verification evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: complete WebSocket JSON to SSE framing, Lite serialized tool calls, and adapter size-error evidence.

## Impact

Responses transport adapters, proxy/bridge integration coverage and OpenSpec. No new settings, dependencies, database migrations or public endpoints. Existing unrelated working-tree changes remain intact.
