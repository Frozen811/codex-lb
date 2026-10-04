## Why

Exactly three registry items (UP-PR-2512, UP-PR-2515, UP-PR-2529) lack local verification. Chat JSON mode still loses its input JSON instruction when requested with equivalent `text.format` controls, and the main specification promises the unsupported original system role.

## What Changes

- Preserve JSON instruction input for both Chat format representations using the existing Responses normalization.
- Correct the Chat contract to keep JSON mentions as developer messages in their original relative position, while hoisting other instructions.
- Specify the existing Business Pro Lite alias and metrics logging compatibility and verify both at product boundaries.
- Repair JSON access records with missing request/status fields and recursive tracing diagnostics during JSON debug startup.
- Add route, real database, and CLI subprocess regression evidence; update only the three selected registry entries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `chat-completions-compat`: equivalent JSON controls and supported developer role normalization.
- `usage-refresh-policy`: canonical Business Pro Lite alias across persistence, capacity, and eligibility.
- `proxy-runtime-observability`: metrics startup and scrapes preserve shared logging, redaction, and file output.

## Impact

The request mapper and shared runtime formatters, focused integration/unit coverage, and OpenSpec/context/registry documentation. No new configuration, dependencies, migrations, dashboard layout, release, or deployment.
