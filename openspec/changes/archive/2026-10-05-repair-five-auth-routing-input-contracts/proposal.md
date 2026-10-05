## Why

Five open registry records (UP-PR-2548, UP-PR-2549, UP-PR-2550, UP-PR-2558, UP-PR-2569) require independent verification in this fork. Current code still caps remote admin sessions below the configured lifetime, divides leased tokens by credits, and hoists developer messages out of durable input.

## What Changes

- Apply the existing role-independent password session lifetime policy to admin sessions.
- Express lease pressure in percentage points per default-size estimated lease; preserve persisted usage for relative-availability fallback and prevent transient pressure from manufacturing exhaustion.
- Preserve developer messages in Responses and compact input, including absent instructions and chained requests; retain system normalization and JSON-mode compatibility.
- Independently exercise existing individual model retrieval and Authorization redaction on their product surfaces, repairing any demonstrated gaps.
- Update exactly the five selected registry rows with verification evidence and retain unrelated existing edits and external limitations.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `admin-auth`: configured password session lifetime applies equally to admin sessions.
- `responses-api-compat`: developer input remains durable and lease pressure has consistent units.
- `account-routing`: relative availability fallback uses persisted usage evidence.

- `proxy-runtime-observability`: explicit Proxy-Authorization values receive the same fail-closed line redaction as Authorization.

Individual model retrieval (`model-catalog-compat`) retains its existing contract and receives fresh verification.

## Impact

Session lifetime resolution, Responses request normalization, account-state construction and balancer selection; focused auth, routing, request, model route and logging tests. Existing routing help/context will reflect the corrected lease-weight unit. No new settings, dependency, migration, deployment, commit or publication is required.
