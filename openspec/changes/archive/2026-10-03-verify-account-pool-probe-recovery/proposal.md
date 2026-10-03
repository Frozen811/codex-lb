## Why

The independent registry has no local verification for UP-PR-2523, UP-PR-2524, and UP-PR-2527. Account inventory, Force Probe settlement, and weekly-only quota recovery need product-path evidence. Inventory availability also needs to respect proven access-credential rejection, which ordinary routing already excludes.

## What Changes

- Verify fresh metrics exposition, refresh failures, and recovery against real database sessions.
- Verify Force Probe settlement after repository teardown and concurrent health observations.
- Align metric availability with the shared credential rejection and expiry predicate.
- Verify weekly-only quota recovery, local cooldown expiry, and preservation of independent rate-limit holds and ownership.
- Expose the existing manual Resume API for quota-exceeded accounts in the dashboard.
- Record focused regression results and close exactly these three local registry entries.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `proxy-runtime-observability`: baseline availability must exclude proven-rejected access credentials while retaining refresh-only warnings.
- `frontend-architecture`: quota-exceeded accounts expose manual Resume with the existing busy and read-only restrictions.

## Impact

Metric publication in `app/modules/proxy/account_cache.py`, the existing dashboard account actions, focused integration and unit tests, owning specs/context and metrics documentation, and `issues-check.md`. Existing Force Probe and account recovery contracts remain authoritative. No new settings, dependencies, schema, or navigation items are introduced.
