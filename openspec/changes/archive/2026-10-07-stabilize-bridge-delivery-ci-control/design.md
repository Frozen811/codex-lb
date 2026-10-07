## Context

The fixture shortens the downstream timeout to 100 ms for the `stall` case. The first ASGI consumer is intentionally paused until its queue closes. The same fixture then sends an independent request to establish that the shared reader is still usable. That control incorrectly retains the 100 ms injected timeout.

## Decisions

Keep the accelerated timeout until closure of the intentionally blocked queue is proven, then restore the fixture's existing ordinary ten-second idle allowance before the independent request. Production still caps downstream enqueue waits at five seconds. Add a 150 ms delay inside only the independent queue's `put` to model scheduler contention within the actual timeout measurement. This must fail with the former fixture timeout and pass with the repaired control.

All original assertions remain: bounded queue slots/bytes, stalled-reader cleanup, one failure terminal, independent successful response, no putter/buffer retention, settled API-key reservations, zero pressure, and healthy account status. Restore fixture patches through pytest's existing monkeypatch lifecycle.

## Risks / Trade-offs

The delayed control adds approximately one second to each of the three stall cases. That cost produces deterministic coverage of the actual CI failure instead of relying on a retry. No application timeout or required cloud gate is weakened.
