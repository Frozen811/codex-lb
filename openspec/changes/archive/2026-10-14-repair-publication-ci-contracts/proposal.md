## Why

Hosted regression jobs expose duplicate timing-column DDL during schema replay, shortened parent bridge retention, and fixtures that predate upstream facets. Dependency auditing also flags the pinned Rust TLS version. These failures block complete fork-main CI.

## What Changes

- Inspect the settings schema before adding the sticky reallocation timing column.
- Preserve an existing column and its values during bootstrap and migration replay.
- Cover both absent and precreated columns through real Alembic upgrade/downgrade paths.
- Verify the startup, legacy replay and restored-store regression paths exposed by hosted CI.
- Apply bridge lifetime shortening only when child lineage supplies an idle cap; preserve ordinary parent alias reuse.
- Update request-log and API-key test fixtures to the published upstream/schema contracts without weakening existing performance assertions.
- Bound SQLite's missing-NULL facet probe before applying row-visibility predicates.
- Update the pinned Rust TLS patch version and lockfile to the advisory-fixed release.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `database-migrations`: define replay compatibility for sticky reallocation timing storage.
- `sticky-session-operations`: make ordinary parent lifetime preservation explicit when reusing a turn-state alias.
- `request-log-upstreams`: preserve bounded legacy facet discovery when upstream metadata is included.

## Impact

The newly introduced timing migration, bridge reuse, affected regression fixtures, TLS dependency manifests, and the two owning specification/context entries. No revision parent, public setting default or historical upstream migration is changed.
