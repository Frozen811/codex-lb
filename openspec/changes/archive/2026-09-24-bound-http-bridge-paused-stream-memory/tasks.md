# Tasks: bound-http-bridge-paused-stream-memory

- [x] 1. Bounded HTTP Bridge Event Queue
  - [x] 1.1 Implement `_HTTPBridgeEventQueue` with `max_events=4096`, `max_bytes=32*1024*1024`, byte tracking, zero-byte sentinel acceptance, lone chunk acceptance, and `close()` support.
  - [x] 1.2 Update `_prepare_response_bridge_request_state` and prewarm in `app/modules/proxy/_service/http_bridge/request_submit.py` to instantiate `_new_http_bridge_event_queue()`.
  - [x] 1.3 Close `event_queue` in `_detach_http_bridge_request` to unblock any pending putters on client disconnect.
- [x] 2. Upstream Reader Backpressure and Stall Handling
  - [x] 2.1 In `app/modules/proxy/_service/http_bridge/upstream_events.py` (`_publish_matched_and_terminal_frames`), handle queue saturation with bounded wait up to `stream_idle_timeout_seconds` or request deadline.
  - [x] 2.2 Handle cancellation on request detachment cleanly so the shared upstream reader is not crashed.
  - [x] 2.3 On stall timeout, fail the request cleanly with `stream_idle_timeout` and `penalize_account=False`.
- [x] 3. Verification & Regression Coverage
  - [x] 3.1 Unit tests for `_HTTPBridgeEventQueue`: event cap, byte budget, zero-byte terminal acceptance, drain-release, empty queue big chunk, and `close()` unblocking.
  - [x] 3.2 Integration tests for paused stream backpressure, resume, detachment, and stall timeout in HTTP bridge.
  - [x] 3.3 Verify migration topology and ruff formatting.

