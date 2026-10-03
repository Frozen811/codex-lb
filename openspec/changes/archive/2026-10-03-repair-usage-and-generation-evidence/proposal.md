## Why

The audit registry has no independently verified closure for UP-PR-2504,
UP-PR-2521 and UP-PR-2444. Existing fixes need transport-to-database evidence;
the HTTP stream's verbatim timing scanner can also miss valid JSON field spacing
or mistake nested metadata for output, distorting output sample qualification.

## What Changes

- Reuse the parsed SSE payload and shared content classifier for verbatim output
  timing, while preserving the forwarded bytes.
- Verify native cache-write accounting through local HTTP/WebSocket upstreams,
  request logs, API-key reservations, read-side costs and repeated settlement.
- Verify optional model-source usage and timings through local upstreams and
  public routes, including fragmented SSE and limited-key failure behavior.
- Verify observed generation timing and reporting independently of reasoning,
  settlement delay and JSON serialization; close exactly the three registry items.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `proxy-runtime-observability`: output sampling uses actual payload fields
  regardless of JSON key spacing/escaping and unrelated nested metadata.

## Impact

`app/modules/proxy/_service/response_timing.py`, focused unit and integration
tests, observability specs/context and `issues-check.md`. Existing pricing,
schema, account ownership and settlement mechanisms are retained. No new
setting, dependency, frontend control or migration is required.
