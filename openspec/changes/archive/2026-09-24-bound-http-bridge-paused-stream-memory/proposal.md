# Proposal: Bound HTTP Bridge Paused Stream Memory

## Why

When a client stops reading an HTTP Responses stream (paused consumer, TCP stall, or slow reader), the HTTP bridge keeps queuing upstream output. Currently:
1. `_WebSocketRequestState` initializes `event_queue = asyncio.Queue()` with `maxsize=0` (unbounded) on both the primary request path (`_prepare_response_bridge_request_state`) and the prewarm path (`_stream_response_bridge_request`).
2. The shared upstream reader in `upstream_events.py` appends received event blocks to `matched_event_queue` without a live-output byte limit or backpressure check.

For long responses or multiple paused clients, worker memory grows without bound, holding tens or hundreds of megabytes of unconsumed events in memory. This can trigger worker out-of-memory crashes and degrade unrelated requests sharing the worker process (Issue #2266).

## What Changes

- Introduce `_HTTPBridgeEventQueue(asyncio.Queue[str | None])`:
  - Enforce a queued-payload byte budget (32 MiB, `_HTTP_BRIDGE_STREAM_QUEUE_BYTES_LIMIT`) alongside an event-count cap (4096, `_HTTP_BRIDGE_STREAM_QUEUE_LIMIT`).
  - Track `queued_bytes` dynamically, updating on enqueue and decrementing on consumer drain (`_get`).
  - Ensure zero-byte events (such as terminal sentinel `None`) are never blocked by the byte budget.
  - Allow an event arriving at an empty queue to be accepted regardless of size so a lone large chunk does not deadlock.
  - Support `close()` to immediately unblock waiting putters and getters when a request is detached or cancelled.
- In `app/modules/proxy/_service/http_bridge/request_submit.py`:
  - Use `_new_http_bridge_event_queue()` for request and prewarm states instead of raw unbounded `asyncio.Queue()`.
  - Call `event_queue.close()` in `_detach_http_bridge_request` to immediately release any blocked upstream putter when downstream disconnects.
- In `app/modules/proxy/_service/http_bridge/upstream_events.py`:
  - When enqueuing to `matched_event_queue`, handle queue saturation: wait for the consumer to drain with a timeout bounded by `stream_idle_timeout_seconds` and the request deadline.
  - If the consumer stays stalled beyond the deadline, fail the request cleanly with `stream_idle_timeout` and `penalize_account=False`.
  - If the consumer detaches while waiting, unblock immediately without crashing the shared upstream reader.

## Capabilities

### Modified Capabilities
- `responses-api-compat`: Bound HTTP responses bridge stream queues by payload bytes and event count, preventing unconsumed output from growing worker memory.

## Impact
- `app/modules/proxy/_service/http_bridge/queues.py` (new bounded queue implementation and size helper)
- `app/modules/proxy/_service/http_bridge/request_submit.py` (use bounded queue, close on detach)
- `app/modules/proxy/_service/http_bridge/upstream_events.py` (backpressure wait and stall handling)
- Tests in `tests/unit/test_http_bridge_event_queue.py` and `tests/unit/test_proxy_http_bridge.py`.
- Fixes #2266.
