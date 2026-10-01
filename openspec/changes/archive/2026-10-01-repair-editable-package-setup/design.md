## Decision

Editable wheels point at the development checkout and are dependency setup, not ready standalone distributions. Skip frontend compilation only for the Hatch editable wheel version. Standard wheel and sdist builds retain fail-closed validation/pinned Bun. Keep frontend compilation explicit in dev and existing Windows workflow; avoid adding Bun to every backend-only job.

## Verification

Use a clean no-asset snapshot with actual uv sync --frozen and the existing incompatible host Bun. Verify no frontend output is produced by dependency setup. Then require a normal wheel build to reject that same toolchain. Validate the custom hook integration through PEP 517, rerun its unit cases, and dispatch exact-head Windows smoke after push.
