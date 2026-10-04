## Why

The three unchecked source rows UP-PR-2508, UP-PR-2513 and UP-PR-2537 need current local evidence. Empty control POSTs still carry a media type, and Images fallback selection can choose the Luna host identified as incompatible with forced image generation; the main image-bypass requirement also omits the implemented bounded-image exception.

## What Changes

- Normalize empty unary control payloads to no body while preserving one media type for nonempty JSON/SDP.
- Remove Luna from Images host candidates while retaining the separate account-probe order.
- Synchronize bounded inline-image bridge admission and reuse in the main Responses contract.
- Add real local HTTP/WebSocket route regressions and close exactly the three registry rows after verification.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: single control media type, bodyless control requests, bounded image admission and retained session behavior.
- `images-api-compat`: Images fallback host compatibility, without changing public image models or account probes.

## Impact

`app/core/clients/proxy.py`, `app/core/openai/host_models.py`, focused unit tests and a new integration suite. Owning specs/context and `issues-check.md` are synchronized. No new settings, dependencies, migrations or dashboard surface; verification uses isolated databases and synthetic local origins, without publication or production changes.
