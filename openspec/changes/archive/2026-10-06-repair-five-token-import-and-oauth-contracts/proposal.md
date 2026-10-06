## Why

Five open registry records (UP-ISSUE-1413, UP-ISSUE-1130, UP-ISSUE-2442, UP-ISSUE-2064, UP-ISSUE-2076) lack independent product-path evidence. Blank access credentials can be imported, a forced refresh of a non-refreshable account returns the rejected credential unchanged, and default Compose publishing occupies the native client's OAuth callback port.

## What Changes

- Reject blank access credentials and normalize empty optional credential fields consistently for auth-file imports and backup restore.
- Fail forced or known-expired non-refreshable preflight without an upstream refresh exchange; preserve normal opaque-token use.
- Verify persisted import, auth status, usage probing, rejection, safe failover, hard ownership, and credential repair through public routes.
- Add an access-token paste mode to the existing dashboard import dialog, requiring explicit email and upstream account identity.
- Stop publishing host port 1455 by default; provide a loopback-only opt-in Compose override and manual/device-login guidance.
- Close exactly the five selected registry scopes with local evidence and preserve prior dirty work.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `account-import`: nonblank access credentials, optional token normalization, non-refreshable preflight boundaries.
- `deployment-installation`: callback-port publication is opt-in for Docker bridge deployments.

## Impact

Auth models and AuthManager, isolated account/proxy regression tests, development and server-only Compose, a small deploy/docker override, published Docker guidance, and corresponding OpenSpec/context. Existing account-routing rejection/ownership contracts are verified without adding redundant requirements. No migrations, dependencies, settings, release, or production changes.
