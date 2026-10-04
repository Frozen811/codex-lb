## Why

Exactly three registry items require independent verification: UP-ISSUE-1844, UP-ISSUE-1843, and UP-ISSUE-1572. Snapshot registration/activation remains outside opt-out serialization, timestamp strings are unconstrained, and shared environment keys are supported by code but absent from the replica topology contract.

## What Changes

- Serialize the complete snapshot protocol and dashboard consent decisions within the process, including registration and activation.
- Validate opt-out timestamps and serialize UTC consistently.
- Align the documented client-family allowlist with supported Codex CLI/Desktop groups and verify database-backed previews.
- Specify and verify existing environment-key precedence, cross-instance decryption, and fingerprint refusal without requiring a mounted key file; make mismatch remediation name both supported key sources.
- Record regression and local runtime evidence for only the three selected registry entries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `telemetry`: full protocol ordering, timestamp validation, and supported client-family aliases.
- `replica-operations`: shared encryption material from environment or file, explicit overrides, and fingerprint consistency.

## Impact

Telemetry sender/API/schema, encryption fingerprint diagnostic, focused integration and unit tests, OpenSpec/context, and issues-check.md. No new settings, dependencies, migrations, dashboard rendering, or collector protocol fields. Cross-process ordering requires collector authority and is outside the local lock guarantee.
