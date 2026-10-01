## Why

Direct WebSocket socket reuse can bypass connect-time account eligibility. An operator Pause can therefore leave a previously selected account serving new turns, even though the routing cache already marks it unavailable. This is a concrete candidate for INC-08, independent of already-running work or traffic outside the proxy.

## What Changes

- Enforce routing availability immediately before each direct WebSocket response.create dispatch, including after asynchronous admission waits.
- Refuse only the unsent turn through existing terminal-error and reservation/lease cleanup paths; preserve other in-flight responses and account ownership.
- Cover real dashboard Pause on both public WebSocket surfaces, including anchored follow-ups and Pause between selection and send.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-routing`: specify the direct WebSocket dispatch boundary for operator routing-unavailable marks.

## Impact

app/modules/proxy/_service/websocket/mixin.py, tests/integration/test_proxy_websocket_responses.py, account-routing spec/context and issues-check.md. No new settings, migrations, external publication or forced cancellation of dispatched responses.
