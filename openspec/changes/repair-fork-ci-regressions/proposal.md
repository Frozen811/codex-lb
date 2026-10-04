## Why

The fork CI runs for 282ce1470, 8f713d322 and 94c9a8c24 failed on route inventory, strict test typing, native compressed-wire decoding and outdated WebSocket error expectations. The integration-core shard also exhausted its job budget while still making progress. A fresh exact-head green run is required before reporting CI repaired.

## What Changes

- Align route and WebSocket regression assertions with existing normative contracts, preserving negative ownership and replay controls.
- Correct test type narrowing and typed doubles without excluding tests or weakening ty rules.
- Decode the native wire probe's request body using its actual Content-Encoding and retain native transport assertions.
- Give the full integration-core slice sufficient bounded execution time while retaining per-test watchdogs and required aggregate checks.
- Diagnose the historical Windows smoke cleanup failure and retain the already-passing newer smoke evidence unless fresh execution exposes a residual.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `release-management`: bounded CI test jobs must preserve complete selected coverage and exact-head required checks.

## Impact

GitHub CI workflow, test contracts and test typing, owning spec/context and issues-check.md. No production configuration, API behavior or schema change is planned. The user's request authorizes a repair commit and publication to fork main to obtain cloud CI evidence.
