## ADDED Requirements

### Requirement: Fork publication requires successful exact-source checks

The independent fork publisher SHALL require an explicit `vX.Y.Z` or `vX.Y.Z-(alpha|beta|rc).N` tag resolving to the current `main` commit. Before publication it MUST validate the newest main-push run for that exact SHA of CI, release guards and simplicity budgets; all three MUST be completed successfully and CI MUST contain a successful `CI Required` aggregate. Missing, pending, cancelled, skipped, failed, stale-SHA or pull-request-only evidence MUST block publication. The publisher MUST recheck source identity and CI after building and before registry login or artifact upload.

#### Scenario: Another SHA has green CI

- **WHEN** the tag's source CI failed but a different commit passed
- **THEN** publication is refused without registry login or artifact upload

#### Scenario: CI is rerun during artifact building

- **WHEN** the initial gate passed but the newest exact-source CI run is pending or failed at the final gate
- **THEN** no artifacts or Docker aliases are published

### Requirement: Fork artifact identity and channels are coherent

The fork publisher MUST check every release-managed version against its tag before building. Wheel and sdist metadata MUST use the equivalent PEP 440 version, packaged application source and runtime MUST match the checked-out source, and both artifacts MUST contain dashboard HTML, JavaScript and CSS. Source distributions MUST exclude local agent worktrees and environment credential files. The loaded image MUST report the tag's version and its OCI revision MUST identify the checked SHA. Packages and image MUST pass isolated readiness and dashboard smoke checks before publication. Exact Docker tags SHALL be the release tag and its version without `v`; only stable releases SHALL additionally update `latest`, `X` and `X.Y`. Prerelease releases MUST be marked prerelease and MUST NOT become GitHub latest. Publishing older stable versions over newer valid stable releases MUST be refused.

#### Scenario: Runtime version differs from the wheel

- **WHEN** a `v1.25.1` candidate contains runtime `1.25.0-beta.9`
- **THEN** it is rejected before building or publishing

#### Scenario: Beta publication preserves stable aliases

- **WHEN** `v1.25.2-beta.1` passes the source and artifact checks
- **THEN** packages report `1.25.2b1`, runtime reports `1.25.2-beta.1`, and only the two exact beta image tags are published

### Requirement: Fork publication preserves provenance and withdraws failures

Fork releases MUST publish checksums and source/CI provenance alongside their wheel and sdist. Existing release assets and exact image tags MUST NOT be silently overwritten. The publisher SHALL be serialized across fork releases. When gating, building, smoke testing or publishing fails or is cancelled, its associated GitHub release MUST be made draft. Mutable stable aliases MUST advance only after package asset upload and exact image publication succeed. The independent fork publisher MUST NOT publish to the upstream PyPI package or upstream registries.

#### Scenario: Source gate rejects a public release

- **WHEN** a published fork release is rejected by its source gate
- **THEN** its release metadata is withdrawn to draft and no new package or image is published

#### Scenario: Publication partially fails

- **WHEN** publication fails after an exact image tag was pushed
- **THEN** the GitHub release is made draft and the workflow reports failure without claiming an atomic rollback of registry artifacts
