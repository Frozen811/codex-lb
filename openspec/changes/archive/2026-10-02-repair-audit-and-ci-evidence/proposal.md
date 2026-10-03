## Why

The next audit items F-007, CI-02 and REL-03 expose unsupported completion claims, CI filters that can omit affected build paths, and fork documentation/release workflows that retain upstream identity or cleanup authority. Users need evidence scoped to source and artifact, and CI must validate the paths actually changed.

## What Changes

- Replace unsupported completion badges and counts with an attributed source inventory and links to independent audit evidence.
- Include renamed source paths and packaging inputs in CI area detection; choose the full suite when PR file evidence is incomplete.
- Render fork documentation with fork repository/edit links and the configured Pages URL; keep upstream release cleanup confined to upstream.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `github-automation`: complete, conservative CI area detection.
- `user-documentation`: scoped verification claims and fork documentation identity.
- `release-management`: upstream release cleanup cannot withdraw fork metadata.

## Impact

CI detector/tests, Docs and upstream Release workflows, MkDocs metadata, README translations and historical claim registries. No application API, database, deployment, release publication or new CODEX_LB setting changes.
