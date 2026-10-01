## Why

INSTALL-01/03/05 lack runtime proof for anonymous public images, optional database profiles and server-only Compose. Production Compose combines a historical registry tag with a source build, so normal startup can ignore checkout fixes. Database profiles do not select the application backend, and a MySQL ping can report health despite rejected credentials.

## What Changes

- Make server-only Compose explicitly build the selected checkout under a local image name; retain zero-config SQLite and document optional external PostgreSQL.
- Require authenticated SQL health probes for development PostgreSQL/MySQL profiles and document service-network versus host URLs.
- Correct existing fork Docker installation/update instructions and disclose historical public image provenance without publishing a replacement.
- Verify isolated public-image, PostgreSQL/MySQL and external PostgreSQL installs, recreation and failed connections.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: Compose source selection, database profile wiring and public image identity.

## Impact

Compose files, existing installation docs/README instructions, focused deployment checks. No new settings, schema changes, public publication or operations on account/production data.
