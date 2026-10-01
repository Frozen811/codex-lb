## Why

INSTALL-02, INSTALL-04 and INSTALL-15 need evidence that local Docker, development Compose and distroless installs work from a clean fork checkout. The extra frontend targets use a different Bun version, build contexts omit exclusions for local agent worktrees and frontend dependency trees, and CI builds only the standard image without an installation smoke.

## What Changes

- Align all frontend container targets with the project's pinned Bun toolchain and protect both build contexts from local dependencies, credentials and agent worktrees.
- Exercise standard and distroless images as non-root installations with readiness, assets, native helper and persistent data after recreate.
- Verify development frontend/backend networking and fresh-clone setup, document the fork source-build path and its boundaries.
- Add distroless build/startup coverage to the existing Docker CI job.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `deployment-installation`: local Docker build, development Compose and distroless installation contracts.

## Impact

Docker build contexts, Dockerfile.distroless, development Compose, Docker CI checks and docs/deployment/docker.md. No public image publication, release version change, production volume operation or account mutation.
