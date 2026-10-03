## Why

SETUP-08/09/10 need observable upgrade/rollback, readiness/failure/shutdown and platform-scope evidence. The update guide assumes origin is the fork even when it is upstream, internal drain authorization relies on projected client identity, and installation health/platform limitations are spread across earlier audit notes.

## What Changes

- Require captured local socket provenance and local effective client identity for internal drain control; prove spoofed forwarded-loopback denial and unchanged local preStop behavior.
- Document explicit fork source selection, cached/pinned image identity and paired rollback rather than a generic origin pull or binary downgrade promise.
- Add startup/readiness/failure/shutdown diagnostics with separate infrastructure, dashboard and upstream/native-helper signals.
- Publish an evidence-scoped platform/topology matrix and distinguish runtime manifests from attestations and flake declarations.
- Rehearse isolated image/source replacement and paired restore, failure modes and Linux signal cleanup; keep production and previous changes intact.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `graceful-shutdown`: internal drain control requires captured local caller provenance.
- `deployment-installation`: source/image update and rollback instructions identify provenance and storage compatibility.
- `user-documentation`: health/failure and platform support claims carry explicit verification scope.

## Impact

Planned code: app/modules/health/api.py, public export of the existing forwarded-hint predicate in app/core/request_locality.py, and corrected missing-dashboard build/reinstall guidance in app/main.py. Tests: protected internal drain route regressions and existing health/drain fixtures; POSIX process tests declare their platform and use bounded startup readiness polling; native-helper discovery fixtures use Windows PATHEXT launchers; upgrade/provenance/doc examples. Guides: COMMUNITY_RELEASE.md update section, docs/deployment/docker.md, docs/deployment/python.md, docs/deployment/kubernetes.md where rollback promises need qualification, docs/troubleshooting.md and docs/getting-started.md for platform coverage. OpenSpec specs/context and issues-check.md. No configuration fields, migrations, release version bumps or publication.
