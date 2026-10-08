## Why

The committed local packages expose six nullable fixture diagnostics in full typing and Windows-specific false failures in artifact persistence, catalog provenance and a real-time Chat probe test. Full fork CI must cover all published code without weakening any existing runtime or provenance gate.

## What Changes

- Preserve the exact committed LF catalog bytes on Windows so historical capture hashes remain valid.
- Keep artifact file flush and atomic replacement while skipping unsupported directory handles on Windows; propagate real POSIX directory errors.
- Stabilize the repeated-capacity Chat probe test with the existing virtual scheduler and unchanged production budgets.
- Add explicit non-null ORM/account fixture assertions for full typing.
- Align three newly exposed integration fixtures with existing credit-evidence and compact slash/capability contracts, exercising the actual wire and fail-closed controls.
- Close the direct WebSocket same-owner retry classifier's missing boolean/nonblank async identity guard, preserving existing owner-bound payload behavior.
- Publish all verified local work to fork main and monitor full exact-SHA CI through success; record failures and repairs separately from historical local closures.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `compatibility-tooling`: host-independent pinned catalog bytes and artifact write durability on supported platforms.
- `responses-api-compat`: valid async identities must be proven before constructing a same-owner fresh resend after anchor loss.

## Impact

`.gitattributes`, `scripts/traffic_analysis/artifacts.py`, the narrow direct WS classifier guard, `tests/unit/test_traffic_artifacts.py`, the single Chat startup regression, six integration fixture files, OpenSpec and publication/registry evidence. No runtime startup timeouts, dependencies, migrations, settings, release tags or production deployment changes.
