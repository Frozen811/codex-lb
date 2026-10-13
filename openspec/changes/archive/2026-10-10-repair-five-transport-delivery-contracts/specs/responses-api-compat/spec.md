## ADDED Requirements

### Requirement: Aggregate live bridge output is bounded

HTTP bridge live queued output MUST share a fixed 256 MiB process-wide UTF-8 payload budget, including payload retained by producers waiting for queue capacity. An enqueue that cannot reserve its payload MUST fail that downstream operation without retaining another waiting payload. Accepted output MUST remain ordered and precede one terminal `response.failed` followed by end-of-stream. Budget exhaustion MUST preserve the shared upstream reader and unrelated requests, and MUST NOT penalize account health for downstream backpressure. Small bounded failure envelopes are terminal metadata outside this live-output budget.

Dequeuing, detachment, cancellation, producer failure and abandoned-queue reclamation MUST release the corresponding payload reservations. Finish or failure MUST release waiting producer reservations while retaining accepted output until delivered or detached. A continuously blocked delivery MUST end within the existing five-second stall bound or the earlier request deadline, independently of a model's long upstream idle allowance.

#### Scenario: Multiple paused streams exhaust the shared budget
- **WHEN** combined queued and waiting-producer payload reaches the process budget
- **THEN** the next payload fails only its downstream operation without another queued or waiting reservation
- **AND** its accepted prefix precedes one failure and end-of-stream
- **AND** unrelated requests and the shared reader remain owned and usable

#### Scenario: Cancellation and detach free admission capacity
- **WHEN** a blocked producer is cancelled or its stream detaches
- **THEN** its payload reservation is released
- **AND** a subsequent enqueue can use the released capacity

#### Scenario: Finished and abandoned queues do not leak payload
- **WHEN** a queue finishes, fails, drains or becomes unreachable
- **THEN** waiting reservations are released on finish or failure
- **AND** accepted payload reservations are released on drain, detach or reclamation

#### Scenario: Long upstream idle budget does not extend a delivery stall
- **WHEN** a downstream queue stays full while the model permits a two-hour upstream idle interval
- **THEN** delivery fails within five seconds or the earlier request deadline
- **AND** the shared reader can continue processing a sibling operation
