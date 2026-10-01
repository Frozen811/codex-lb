## Why

Full PR CI revealed that Nix's explicit source filters omit the custom Hatch build hook declared by pyproject.toml. Nix wheel creation fails before it can reuse its prebuilt frontend assets. The editable metadata source has the same missing-hook seam.

## What Changes

- Include only the declared Hatch hook and its stdlib dashboard helper in package and editable source filters.
- Preserve explicit source filtering and Nix's existing prebuilt frontend/editable semantics; verify the actual Nix CI build before archiving.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: complete build-hook inputs in filtered Nix sources.

## Impact

flake.nix source filesets only; no dependency/input lock update, runtime settings or published artifact change.
