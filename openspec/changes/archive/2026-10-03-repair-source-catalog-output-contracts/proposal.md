## Why

UP-PR-2525, UP-PR-2526 and UP-PR-2528 lack independent closure in the audit
registry. Source instructions and collaboration declarations are implemented
but absent from the main requirements; malformed output limits can override
the GPT-6 compatibility fallback with booleans or nonpositive counts.

## What Changes

- Verify source instructions through persisted dashboard configuration and
  both native catalog routes, preserving whitespace and Unicode.
- Synchronize the implemented nonblank collaboration-version contract and
  verify complete namespaces and matching choices at a recording upstream.
- Require positive, non-boolean integer output limits before using upstream
  precedence; retain the existing 128000 fallback for the three GPT-6 slugs.
- Record red-before/green-after regression evidence and close exactly three
  local audit entries, preserving public/cloud residuals.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `model-catalog-compat`: source instruction projection and valid GPT-6 output
  budgets on compatible catalog/retrieval surfaces.
- `responses-api-compat`: source collaboration namespace opt-in from a
  nonblank version declaration.

## Impact

`app/modules/proxy/api.py`, focused catalog/collaboration integration tests,
owning specs/context and `issues-check.md`. No dependencies, settings,
migrations, dashboard rendering or generation defaults are added.
