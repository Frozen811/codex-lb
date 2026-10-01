## 1. Build context and toolchain (INSTALL-02)

- [x] 1.1 Exclude local and nested workstation state in root/frontend contexts and verify real BuildKit export with inert forbidden files and required inputs.
- [x] 1.2 Align all container Bun versions with frontend/package.json and verify standard linux/amd64 build plus non-root/readiness/assets/native/CA checks.
- [x] 1.3 Recreate the standard container with its isolated named volume and verify synthetic stored data and encryption-key hash persist.

## 2. Development Compose (INSTALL-04)

- [x] 2.1 Verify clean no-env Compose config and frontend/backend build/start with isolated volumes/ports, checking the dashboard and proxy readiness path.
- [x] 2.2 Exclude local frontend env/dependencies from watch and verify watch configuration and host-to-container source sync.
- [x] 2.3 Run the frontend as non-root and repeat startup/proxy/watch tests to prove writable source and Vite cache paths.

## 3. Extra targets (INSTALL-15)

- [x] 3.1 Build distroless and verify non-root/readiness/assets/native/CA, shell-free diagnostics and persistent-volume recreation.
- [x] 3.2 Add standard/distroless startup smoke to existing Docker CI; verify actionlint and focused workflow/deployment regressions.

## 4. Documentation and closure

- [x] 4.1 Document actual fork source-build/development/distroless commands in the owning docs/context, with tested platforms and remaining install boundaries.
- [x] 4.2 Update issues-check with findings/evidence, run strict OpenSpec and relevant checks, sync/verify/archive locally without claiming cloud publication.
