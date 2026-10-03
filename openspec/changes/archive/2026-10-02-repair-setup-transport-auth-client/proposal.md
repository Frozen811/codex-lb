## Why

SETUP-05/06/07 need transport, authentication and actual client-path evidence. Proxy projection appears to conflate the caller with the identity-asserting proxy, OAuth bind failures discard an initialized listener without cleanup/diagnostics, and client setup contains a conflict marker and ambiguous auth/usage examples.

## What Changes

- Authorize trusted-header evidence by the captured socket peer, preserving forwarded caller identity for locality and firewall decisions.
- Clean up callback listener resources on failed startup; retain manual callback behavior and report a safe diagnostic.
- Document tested TLS/proxy trust and separate client auth/config paths; remove conflict residue and verify endpoint suffixes.
- Rehearse direct/proxied SSE and WebSocket, remote bootstrap/API keys, synthetic OAuth/import and installed Codex generation/routing/quota/Pause using isolated stores and a synthetic upstream.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `admin-auth`: trusted-header authorization uses socket provenance.
- `oauth-callback-privacy`: failed listener startup releases resources without exposing callback credentials.
- `deployment-networking`: TLS proxy setup identifies both forwarding trust layers and transport verification boundaries.
- `user-documentation`: client setup distinguishes provider auth, endpoint suffixes and observed client version.

## Impact

Planned code: app/core/auth/dashboard_mode.py, app/core/middleware/dashboard_auth_proxy.py, app/modules/oauth/service.py. Tests: trusted-header route regressions, OAuth bind/cancellation cleanup regressions and client-example validation; test_proxy_websocket_client.py proxy-env setup reordered for Windows case-insensitive aliases. Guides: docs/client-setup.md, docs/examples/codex/config.toml, docs/deployment/remote.md, docs/getting-started.md and docs/authentication.md as needed by observed behavior. Owning OpenSpec/context and issues-check.md. Existing local changes retained; no production store, login, publication, new settings or schema changes.
