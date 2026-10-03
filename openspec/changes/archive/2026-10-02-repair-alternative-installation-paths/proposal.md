## Why

INSTALL-12/13/14 still route users to upstream artifacts or undocumented service management. Helm installs with chart-managed credentials can deadlock with `--wait` because the schema gate waits for a post-install migration that Helm cannot start before readiness.

## What Changes

- Select the fork in Helm defaults and Nix guidance, and identify source versus historical public artifacts explicitly.
- Run fresh-install migrations that need chart-created credentials as ordinary Jobs; retain pre-upgrade migration ordering and pre-install hooks where all credentials already exist.
- Provide a concrete streaming reverse-proxy example and remove the unsupported systemd restart assumption.
- Validate disposable Kubernetes installs, Nix startup and remote access; record coverage boundaries in the audit registry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: fork artifact selection and deadlock-free Helm install migration ordering.
- `deployment-networking`: executable reverse-proxy guidance preserves streaming and dashboard request identity.

## Impact

Helm metadata, values, migration templates and smoke tests; flake metadata; README translations and deployment guides; COMMUNITY_RELEASE update instructions. No API/schema changes, settings additions, dashboard navigation changes or release publication.
