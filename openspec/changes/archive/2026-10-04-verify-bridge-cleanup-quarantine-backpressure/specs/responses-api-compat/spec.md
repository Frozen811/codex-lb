## MODIFIED Requirements

### Requirement: Retry Circuit Scheduled Purge Fencing
The durable bridge repository scheduled purge for stale retry circuits (`purge_retry_circuits_before`) SHALL fence each deletion against the selected observation timestamp, admission generation and consecutive failure count. A candidate changed between selection and deletion SHALL NOT be selected again in the same cleanup pass. Unchanged old rows SHALL remain eligible under the existing age and continuity rules.

#### Scenario: Stale retry circuit candidate updated before deletion
- **GIVEN** a stale candidate observed at timestamp T0, generation G0 and failure count F0
- **WHEN** a concurrent operation changes any of those values before deletion
- **THEN** that cleanup deletion matches zero rows
- **AND** the candidate survives the entire cleanup pass, including when other candidates are deleted successfully

#### Scenario: Lagging-clock failure preserves the timestamp
- **GIVEN** a stale candidate observed at timestamp T0 and failure count F0
- **WHEN** a newer failure increments the count without advancing T0
- **THEN** scheduled cleanup preserves that row

### Requirement: Bounded Memory for Paused HTTP Bridge Streams
Events emitted by the HTTP Responses bridge for an active downstream stream MUST be buffered in a queue bounded by both a queued-payload byte budget (32 MiB) and an event-count cap (4096). Queued bytes MUST be released dynamically as the downstream consumer drains events.

When a downstream consumer pauses or stops reading, unconsumed live output MUST NOT exceed the byte budget or event cap except for one event arriving at an empty queue. If the queue is saturated:
1. The shared upstream reader MUST pause enqueueing until the downstream consumer drains sufficient bytes or events.
2. A zero-byte event MUST NOT be rejected by the byte budget as long as the event cap has room.
3. An event arriving at an empty queue MUST be accepted regardless of size.
4. A blocked delivery MUST wait no longer than the minimum of five seconds, `stream_idle_timeout_seconds`, and the remaining request deadline (with the existing 0.1-second scheduling floor for an elapsed deadline). On expiry the proxy MUST preserve already accepted output order, then deliver one `response.failed` with `stream_idle_timeout`; it MUST NOT report downstream success or penalize the upstream account for the delivery failure.
5. Downstream disconnect or detachment MUST release the queued bytes and unblock waiting upstream putters without cancelling the shared reader.
6. A terminal sentinel MUST finish delivery without waiting for an event-cap slot or replacing an already accepted success terminal with a delivery failure. One pending synthetic failure terminal SHALL have a bounded memory cost independent of the output queue.

#### Scenario: Downstream consumer pauses and resumes
- **GIVEN** an active HTTP bridge response stream with a bounded event queue
- **WHEN** the consumer pauses until the queue is saturated and resumes before the delivery bound
- **THEN** enqueueing resumes and buffered output is delivered in order

#### Scenario: Downstream consumer stays stalled beyond timeout
- **GIVEN** a saturated stream queue and a two-hour model idle allowance
- **WHEN** the consumer remains paused for five seconds
- **THEN** the producer stops waiting and the shared reader can process other requests
- **AND** a resumed consumer receives accepted output followed by one `stream_idle_timeout` failure
- **AND** the account health is not penalized and the reservation settles

#### Scenario: Downstream client disconnects while queue is saturated
- **GIVEN** an upstream reader waiting for space in a saturated stream queue
- **WHEN** the downstream client disconnects or is cancelled during the ASGI send
- **THEN** the response iterator and its nested bridge iterator close explicitly
- **AND** queued bytes are released, the producer is unblocked and reservation cleanup completes

#### Scenario: Terminal sentinel after a saturated success
- **GIVEN** a queue whose last available event slot holds an accepted success terminal
- **WHEN** the producer finishes delivery
- **THEN** completion does not wait for another event slot
- **AND** the consumer receives that success terminal followed by end of stream

## ADDED Requirements

### Requirement: Detached bridge queues release output and waiters
A detached HTTP bridge stream SHALL release queued payload references and byte accounting immediately. Cancelled producers SHALL release their queue waiters. Queue shutdown caused by downstream detachment SHALL NOT cancel the shared upstream reader; cancellation of the reader itself SHALL still propagate.

#### Scenario: Detachment during a blocked enqueue
- **GIVEN** a saturated downstream event queue and an upstream producer waiting for room
- **WHEN** the downstream request detaches
- **THEN** the queue discards queued output and unblocks its producer
- **AND** unrelated requests continue through the shared reader

#### Scenario: Producer cancellation leaves no waiter
- **WHEN** a producer is cancelled while waiting for queue capacity
- **THEN** its waiter and retained payload are released
- **AND** the next producer can proceed after capacity becomes available
