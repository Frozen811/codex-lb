## Why

Five open registry records lack verified fork evidence. Reconnects can lose prewarm context, reject complete same-owner agent history, or strand an unavailable policy-excluded owner; Desktop voice setup omits the independent call and sideband overrides.

## What Changes

- UP-PR-2562: document both experimental Desktop voice overrides and verification boundaries.
- UP-PR-2572: verify existing persisted quota reset and idle recovery without importing the obsolete branch.
- UP-PR-2575: retain empty prewarm context evidence and reject incomplete unanchored WebSocket replay.
- UP-PR-2581: accept valid agent follow-ups only in durable same-owner context proofs, retaining the original body and account pin.
- UP-PR-2583: consider policy-conflict retirement only when durable owner availability and request deadline permit it.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: prewarm replay and same-owner agent history.
- `sticky-session-operations`: policy-excluded owner retirement under existing durable guards.
- `realtime-api-compat`: documented Desktop client configuration and verification limits.

## Impact

Proxy replay helpers, HTTP bridge and WebSocket paths, focused public-route regressions, Live Voice documentation, and exactly five issues-check.md source records. No new settings, migrations, dependencies, dashboard changes or publication.
