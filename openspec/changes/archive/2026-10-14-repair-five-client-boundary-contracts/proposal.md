## Why

Five open registry entries describe client boundary failures: rejected transparent image requests, native WebSocket bursts discarded at 65 frames, uncaught OAuth connection errors, weekly-only quota recovery, and CCodex fingerprint/package compatibility. This batch owns exactly UP-PR-2589, UP-PR-2593, UP-ISSUE-2594, UP-ISSUE-2601 and UP-ISSUE-2602.

## What Changes

- Accept transparent PNG/WebP images while rejecting transparent JPEG before dispatch.
- Replace the native WebSocket's 64-message cliff with bounded payload accounting and a generous event cap, preserving ACK progress, FIFO and terminal cleanup.
- Translate direct OAuth network failures into sanitized OAuth errors while propagating cancellation.
- Verify and repair weekly-only Pro Lite recovery without bypassing cooldown or concurrent account status changes.
- Verify the existing exact CCodex identity allowlist through HTTP and WebSocket routes; require the patched urllib3 minimum for package installs.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `images-api-compat`: transparent output format compatibility.
- `responses-api-compat`: bounded native WebSocket buffering and CCodex identity preservation.
- `oauth-callback-privacy`: safe network failures and terminal callback state.
- `usage-refresh-policy`: weekly-only Pro Lite recovery.

## Impact

Application edits are scoped to app/core/openai/images.py, app/core/clients/native_egress.py, app/core/clients/oauth.py and, if the regression demonstrates a gap, app/modules/usage/updater.py. Dependency metadata changes are limited to pyproject.toml and uv.lock. Focused tests use tests/unit/test_native_websocket_buffering.py, tests/unit/test_oauth_transport_errors.py, tests/unit/test_images_schemas.py, tests/integration/test_proxy_images.py, tests/integration/test_oauth_flow.py and tests/integration/test_client_boundary_contracts.py. Canonical spec/context files for the four capabilities and issues-check.md will be synchronized. Existing dirty account placement files are preserved. No publication or deployment is included.
