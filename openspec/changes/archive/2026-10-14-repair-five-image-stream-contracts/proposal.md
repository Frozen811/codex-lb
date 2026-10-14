## Why

Exactly five unchecked registry rows (UP-ISSUE-2304, UP-ISSUE-620, UP-ISSUE-1950, UP-ISSUE-1711 and UP-PR-2520) need independent local verification. Images collection can currently replace an already completed result with a trailing incomplete event, and the Images spec contains contradictory host selection requirements.

## What Changes

- Preserve the first completed image result while draining trailing events for cleanup and accounting.
- Align the obsolete duplicate Images host requirement with the existing compatible-host requirement.
- Verify Image 2.5 generation/edit aliases, bounded fan-out and settlement, hosted screenshot slimming, authentic WebSocket errors and the lazy streaming entrypoint.
- Close only the five selected registry rows using exact local evidence.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `images-api-compat`: completed Images response precedence and removal of contradictory host selection requirements.

## Impact

Images translation and focused tests; existing Responses/WebSocket product-path suites; Images spec/context and issues-check.md. No configuration, dependency, schema or publication changes.
