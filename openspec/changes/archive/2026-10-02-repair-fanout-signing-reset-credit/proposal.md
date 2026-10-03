## Why

INC-04-FANOUT, INC-05-SIGNING, and INC-06-RESET remain unverified in the audit registry. Image fan-out can discard completed usage on cancellation or request-log failure, while bridge key precedence and cross-account reset refusal need product-path evidence.

## What Changes

- Preserve successful image subcall usage through partial failures, cancellation, and request-log errors; drain all owned subcalls before returning.
- Verify bridge signatures across independent replica settings with shared environment/file keys and reject differing keys.
- Verify missing cross-account identity refusal through all consume ingress aliases with no dispatch or credit mutation.
- Record tests and update exactly these three registry items.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `images-api-compat`: fan-out usage and cancellation ownership.
- `bridge-ring-membership`: configured shared-key signing precedence.
- `usage-refresh-policy`: cross-account reset identity refusal.

## Impact

Image fan-out implementation and targeted integration tests; existing bridge crypto and reset handlers; owning OpenSpec context and issues-check.md. No new settings, migrations, or dependencies.
