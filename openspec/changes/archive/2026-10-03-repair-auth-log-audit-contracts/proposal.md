## Why

Independent checks for UP-ISSUE-2028, UP-PR-2487 and UP-PR-2490 remain open. The current authorization redactor attempts to distinguish credential parameters from diagnostic text and can retain credential tails; TOTP and refresh diagnostics already have source fixes that need independent product-path verification.

## What Changes

- Mask an unquoted authorization value through the end of its current line. Mask a complete quoted value without consuming the surrounding field context.
- Exercise original adversarial authorization examples through error fields, text/JSON formatters and exception rendering.
- Expand Unicode TOTP route checks and verify failed refresh diagnostics against an actual local OAuth HTTP server.
- Record evidence for exactly the three selected registry items.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `proxy-runtime-observability`: explicit authorization field redaction overrides the old same-line separator policy, preserving line boundaries and idempotency.

## Impact

Runtime log redaction and focused tests; existing admin-auth and account-routing contracts are verified without production changes. No new dependencies, configuration or dashboard rendering. No publication or deployment.
