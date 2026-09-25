# Capability: Responses API Compatibility

## ADDED Requirements

### Requirement: Bounded Memory for Paused HTTP Bridge Streams
Events emitted by the HTTP Responses bridge for an active downstream stream MUST be buffered in a queue bounded by both a queued-payload byte budget (32 MiB) and an event-count cap (4096). Queued bytes MUST be released dynamically as the downstream consumer drains events.

When a downstream consumer pauses or stops reading, unconsumed live output MUST NOT exceed the configured byte budget or event cap. If the queue is saturated:
1. The shared upstream reader MUST pause enqueueing until the downstream consumer drains sufficient bytes or events.
2. A zero-byte event (such as the terminal sentinel `None`) MUST NOT be rejected by the byte budget as long as the event cap has room.
3. An event arriving at an empty queue MUST be accepted regardless of size.
4. If the downstream consumer stays stalled longer than `stream_idle_timeout_seconds` or the request deadline, the proxy MUST fail the request with `stream_idle_timeout` and MUST NOT penalize the upstream account.
5. If the downstream consumer disconnects or detaches, waiting upstream putters MUST be unblocked immediately without crashing the shared upstream reader.

#### Scenario: Downstream consumer pauses and resumes
- **Given** an active HTTP bridge response stream with a bounded event queue
- **When** the downstream consumer stops reading and queued events reach the 32 MiB byte budget
- **Then** subsequent upstream events pause enqueueing without growing worker memory
- **When** the downstream consumer resumes reading and drains queued events
- **Then** upstream enqueueing resumes and subsequent events are delivered to the consumer.

#### Scenario: Downstream consumer stays stalled beyond timeout
- **Given** an active HTTP bridge response stream whose queue is saturated
- **When** the downstream consumer does not drain any events before `stream_idle_timeout_seconds` expires
- **Then** the request is failed with `error.code = "stream_idle_timeout"`
- **And** the upstream account health is NOT penalized.

#### Scenario: Downstream client disconnects while queue is saturated
- **Given** an upstream reader waiting for space in a saturated stream queue
- **When** the downstream client disconnects and the request is detached
- **Then** the event queue is closed and the waiting upstream reader is unblocked immediately
- **And** the shared upstream reader continues running without crashing.
