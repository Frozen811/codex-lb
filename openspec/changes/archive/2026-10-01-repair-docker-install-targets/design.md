## Context

The standard image was smoke-tested in the prior release batch, but local installation context, volume recreation and the extra targets remain unchecked. Development Compose and distroless use Bun 1.4.2 while frontend/package.json pins 1.3.14. Baseline builds of both extra targets succeed; the version drift is not an image-not-found failure.

## Goals / Non-Goals

Verify INSTALL-02/04/15 on Docker Desktop Linux/amd64 from Windows. Preserve existing user volumes and running services. Public GHCR aliases, production external databases, Helm, real OAuth/Codex traffic and ARM64 are separate audit items.

## Decisions

- Keep the existing Dockerfiles and inline frontend target, align Bun to 1.3.14, add a frontend-specific ignore file and extend the root ignore policy.
- Validate ignore semantics using actual BuildKit COPY/export with inert synthetic files, including nested env/worktrees/dependencies; no real secrets are copied for the test.
- Exercise readiness/assets with shared release smoke; check native helper, CA trust, non-root identity and named-volume recreation with synthetic persistent data.
- Development Compose audit uses explicit temporary overrides for random loopback ports and every named volume because the stock volume names are fixed and a project prefix alone does not isolate them.
- The inline frontend inherited UID 0 from the Bun image; run install and Vite as bun with owned WORKDIR/source/dependency cache. Repeat the full startup/proxy/watch test to catch permission regressions.
- Extend the existing Docker CI job with a second build and isolated readiness/assets smoke; preserve its standard-image Trivy gates. A full vulnerability report is distinct from an installation proof.

## Risks / Trade-offs

Additional CI build time is bounded by shared BuildKit caches. Non-root volumes use image initialization ownership; arbitrary host bind mounts need operator-provided matching permissions. Local dirty-tree evidence cannot prove published artifacts or new cloud checks. Distroless diagnostics use Python rather than a shell.
