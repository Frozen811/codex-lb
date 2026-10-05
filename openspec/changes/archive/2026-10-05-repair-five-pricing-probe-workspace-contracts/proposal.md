## Why

Five open registry items leave confirmed Ultrafast usage underpriced, Helm startup timing fixed, terminal SQLite writes cancelled at the delivery bound, CCodex identities rewritten, and deactivated workspaces eligible for repeated selection. Repair these bounded contracts while preserving existing local work.

## What Changes

- UP-PR-2547: preserve explicit Ultrafast prices, including cache writes and long context, and settle exact microdollars using the effective response tier.
- UP-PR-2553: expose validated Helm startup-probe timing with unchanged defaults and a fixed handler.
- UP-PR-2555: keep terminal append tasks owned after timeout or caller cancellation; retain settlement and late-commit fences.
- UP-ISSUE-2560: recognize the two CCodex gateway identities through the shared native classifier.
- UP-PR-2573: exclude only the workspace named by an exact upstream deactivation code and fail over only before visibility and without hard ownership.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `upstream-metadata`: validated Ultrafast catalog groups and offline preservation.
- `api-keys`: effective-tier monetary settlement without float roundtrip loss.
- `deployment-installation`: optional startup-probe timing and schema validation.
- `responses-api-compat`: detached owned terminal writes and CCodex native identity.
- `account-routing`: workspace exclusion and safe failover.
- `usage-refresh-policy`: workspace-specific exclusion survives refresh.

## Impact

Pricing/catalog/snapshot, API-key settlement, shared client header classifier, bridge event batcher, failover policy/classifier/stream health ordering, Helm values/schema/template, focused regression tests, and existing capability context. No migrations, dependencies, application settings, navigation, publication, or production actions. Existing cache-write accounting and newer failover-walk semantics remain intact.
