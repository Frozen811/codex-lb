## Why

Three independently unchecked registry items (#2356, #2128, #2038) concern native client compatibility. Existing routes lack complete transport/visibility evidence, search trailing slashes return 405, and single-model trailing slashes become part of the model ID.

## What Changes

- Support standalone search with and without a trailing slash on canonical and v1 ingress.
- Support a trailing slash on single-model retrieval while preserving identifiers containing slashes and catalog visibility.
- Verify all native history/notes operations preserve bodies, queries, encryption headers, authentication and affinity through actual HTTP routes.
- Record bounded local evidence in each selected issues-check entry.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `responses-api-compat`: specify search aliases and slash equivalence.
- `model-catalog-compat`: specify individual-model retrieval parity and slash behavior.
- `native-history-notes-proxy`: specify opaque transport parity across ingress aliases.

## Impact

`app/modules/proxy/api.py`; integration tests for native notes, search and models; owning specs/context; `docs/client-setup.md`; `issues-check.md`. No settings, schema migration, dependencies or release changes.
