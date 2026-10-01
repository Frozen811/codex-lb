## Why

The exact-head Windows diagnostic run 36904727598 failed before tests: uv sync installs the checkout as editable before the workflow builds the frontend. The new distribution asset hook accidentally imposed Bun on this dependency-setup path. Backend CI and development environments must remain able to install dependencies independently of frontend compilation.

## What Changes

- Limit the dashboard requirement to distributable package builds; editable development installs leave frontend compilation to the existing frontend step.
- Reproduce actual no-asset uv sync without the pinned Bun prerequisite and retest non-editable refusal/build behavior.
- Run the Windows diagnostic again on the corrected published source and record both attempts.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: editable setup versus complete distribution build contract.

## Impact

Custom Hatch hook and installation context/docs, with no runtime setting or weakening of distributable asset validation.
