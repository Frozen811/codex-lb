## Context

HTTP streaming already reanchors its attempt clock after admission and persists existing phase columns. `ParsedSseBlock` distinguishes a local event from a real upstream event with a synthesized response ID. Sampling currently ignores that distinction. The bridge has both an obsolete eventless-only health contract and its post-output replacement.

## Goals / Non-Goals

Prove the three selected registry contracts through existing transport, API, persistence and metric paths. Do not alter replay, settlement, schema, metric labels or native worker behavior. Native macOS execution remains a platform-specific verification boundary.

## Decisions

- Gate HTTP phase sampling at the stream consumer using the event type and carrier's `is_local` flag; do not use `response_id_is_local`, because upstream errors may receive a local ID. Keep shared WebSocket output sampling unchanged.
- Preserve verbatim relay and original lazy pull behavior. Sampling uses the already parsed payload and adds no persistence barrier.
- Remove the superseded eventless-only requirement; retain the later abrupt-drop contract, including windowed eventless drain and penalties for protocol-invalid/authored-close failures.
- Verify the existing closed-port native fallback fix with the real helper and unchanged completion/error, owner, cleanup and no-replay assertions.

## Risks / Trade-offs

Unmarked plain strings are assumed to be upstream events when they have an event type, matching the existing producer contract. Loopback tests establish transport behavior on the executed platform; they do not establish macOS or hosted-provider behavior.
