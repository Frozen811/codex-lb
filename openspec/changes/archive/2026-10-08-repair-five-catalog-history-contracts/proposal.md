## Why

Five unverified registry rows cover native catalog and account-local control contracts. The startup catalog omits Astra, history/notes ignore the native body session identity, and featured-plugin trailing slashes redirect instead of forwarding.

## What Changes

- Repair UP-PR-2445 plugin ingress aliases and trailing-slash behavior.
- Repair UP-PR-2101 native body-session ownership without changing Responses affinity.
- Implement UP-PR-2085 captured Astra bootstrap metadata and existing model-label normalization.
- Verify UP-ISSUE-1467 Spark discovery across refreshed and restored registry state.
- Verify UP-PR-2543 shipped and inline authenticated model-discovery configuration.
- Close exactly these five local registry scopes with regression evidence.

## Capabilities

### Modified Capabilities

- `native-history-notes-proxy`: body-session identity, immutable account ownership, opaque data preservation.
- `model-catalog-compat`: captured Astra bootstrap metadata and preserved Spark/discovery contracts.
- `responses-api-compat`: Astra label normalization and plugin catalog passthrough.
- `api-firewall`: protect equivalent plugin catalog ingress.

## Impact

Proxy routes/control service, affinity source typing, registry bootstrap, request policy, focused unit/API tests, owning OpenSpec contexts and issues-check.md. No schema, settings, dependency, release or deployment changes.
