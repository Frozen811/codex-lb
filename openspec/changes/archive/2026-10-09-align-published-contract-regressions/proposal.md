## Why

Fork CI #90 exposed four regression tests that still assumed contracts predating the published catalog and routing repairs. The full suite must verify the current control-adapter signature, complete route inventory, transport framing, and independent account ownership.

## What Changes

- Record and assert the new optional control-adapter arguments in the alpha-search route test.
- Classify and exercise all published plugin aliases under the existing capability-denial policy.
- Verify unchanged HTTP SSE bytes and canonical WebSocket-to-SSE serialization while retaining semantic usage, timing, settlement, and accounting assertions.
- Give the owner-bound coded-429 test independent tool-continuation state so ciphertext-only quota failover does not invalidate its premise.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

None. This change adjusts regression coverage to existing normative contracts; `skip_specs: true` records the absence of product behavior changes.

## Impact

Four Python test files and this verification change. No application code, dependencies, migration, configuration, or public API changes.
