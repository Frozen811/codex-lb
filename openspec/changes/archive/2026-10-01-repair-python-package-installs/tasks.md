## 1. Public packages

- [x] 1.1 Refresh wheel/sdist downloads, hashes and archive contents; correlate root application code with the release tag.
- [x] 1.2 Install public wheel and public sdist in clean environments and check runtime, CLI, readiness/assets, data paths and migrations outside the checkout.

## 2. Source and tool installation

- [x] 2.1 Reproduce a dashboard-less wheel from clean Git source, then add a fail-closed frontend build hook with pinned Bun/frozen lock and complete asset validation.
- [x] 2.2 Verify package, sdist rebuild and source/Git installation without workstation state; cover missing/wrong Bun and failed/incomplete frontend builds.
- [x] 2.3 Exercise isolated uvx and uv tool fork installation/updates and document the upstream index boundary.

## 3. Documentation and publication

- [x] 3.1 Correct existing README/translation/getting-started/update commands and add spec-owned Python installation guidance.
- [x] 3.2 Record evidence/limits, focused tests and strict OpenSpec, sync/verify/archive locally.
- [x] 3.3 Commit the authorized accumulated fixes in coherent groups, push the fork branch and verify remote source/available Actions state.
