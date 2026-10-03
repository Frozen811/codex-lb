# release-management Specification

## Purpose
Governs the release channels of codex-lb: the stable path owned by release-please and the PR-driven beta channel layered on it. Beta releases must be prepared through release PRs, publish as GitHub prereleases on merge, never advance stable aliases or the stable manifest, and withdraw public release metadata when publishing fails, so stable promotion stays release-please owned and every release-managed version field is guarded.

## Requirements

### Requirement: Beta releases are prepared through release PRs

Beta releases SHALL be prepared by an automatically maintained pull request against `main` that updates the release-managed version files to `X.Y.Z-beta.N`. The beta preparation flow SHALL run after release-please completes and after pushes to `main`, SHALL derive `X.Y.Z` from the open release-please PR branch, and SHALL do nothing when there is no open release-please PR. Beta release PRs SHALL NOT update `.github/release-please-manifest.json` because stable version ownership remains with release-please.

#### Scenario: automation syncs the next beta from the release-please PR

- **GIVEN** release-please has opened or updated `release-please--branches--main` with `pyproject.toml` version `1.19.0`
- **WHEN** the beta PR sync workflow runs
- **THEN** it creates or updates a pull request that sets release-managed files to `1.19.0-beta.N`
- **AND** `N` is one higher than the highest existing `v1.19.0-beta.N` tag
- **AND** `.github/release-please-manifest.json` remains unchanged

#### Scenario: automation is idle without a release-please PR

- **GIVEN** there is no open release-please PR targeting `main`
- **WHEN** the beta PR sync workflow runs
- **THEN** it exits without creating a beta release pull request

#### Scenario: automation ignores forked release-please branch names

- **GIVEN** a fork has an open pull request whose head branch is named `release-please--branches--main`
- **WHEN** the beta PR sync workflow looks for the release-please PR
- **THEN** it ignores that pull request unless the head repository owner is the canonical repository owner
- **AND** it requests enough open pull requests to avoid missing the canonical release-please PR during high-PR-volume periods

#### Scenario: merged beta release already covers main

- **GIVEN** tag `v1.19.0-beta.1` points to `HEAD`
- **AND** release-managed files all contain `1.19.0-beta.1`
- **WHEN** the beta PR sync workflow runs for base version `1.19.0`
- **THEN** it exits without creating `1.19.0-beta.2`

#### Scenario: automation-generated beta PR starts unvalidated

- **GIVEN** the beta PR sync workflow creates or updates `release/beta-1.20.0-beta.3`
- **WHEN** it writes the pull request body
- **THEN** the body includes a `Release-candidate validation` section
- **AND** the section records the exact beta PR head SHA as the validated candidate placeholder
- **AND** backend, frontend, wheel/package, Docker/container, and live upstream/account smoke checklist items start unchecked

### Requirement: Merged beta release PRs publish GitHub prereleases

When a pull request from a `release/beta-*` branch is merged into `main`, the release automation SHALL require `RELEASE_PLEASE_TOKEN` rather than falling back to `GITHUB_TOKEN`, verify that all release-managed version files agree on a beta version, require release-candidate validation evidence for the exact merged pull request head SHA, verify that the published merge commit tree matches that validated head tree, create the matching `vX.Y.Z-beta.N` tag at the merge commit, and publish a GitHub prerelease for that tag. Re-running the workflow after the tag already exists SHALL be safe and SHALL NOT create a second tag. Before merge, the beta release guard SHALL require release-candidate validation evidence for canonical `release/beta-X.Y.Z-beta.N` pull requests whose checked-out tree already contains the matching beta version, even when the release-managed version files are unchanged relative to the base branch.

#### Scenario: beta PR merge publishes a prerelease tag

- **GIVEN** a merged pull request from `release/beta-1.19.0-beta.1`
- **AND** release-managed files all contain `1.19.0-beta.1`
- **AND** the pull request body contains checked release-candidate validation evidence for the exact merged pull request head SHA
- **AND** the merge commit tree matches the validated pull request head tree
- **AND** `RELEASE_PLEASE_TOKEN` is configured
- **WHEN** the beta publish workflow runs
- **THEN** it creates tag `v1.19.0-beta.1` at the merge commit
- **AND** it creates a GitHub prerelease for `v1.19.0-beta.1`

#### Scenario: inconsistent release metadata is blocked

- **GIVEN** a pull request changes one or more release-managed version files
- **AND** the release-managed files do not all contain the same version
- **WHEN** the CI beta release guard runs
- **THEN** it fails before deciding whether the change is stable or beta
- **AND** it reports the mismatched release-managed file versions

#### Scenario: canonical beta PR with unchanged metadata still requires validation

- **GIVEN** `main` already contains release-managed files set to `1.20.0-beta.3`
- **AND** a pull request from `release/beta-1.20.0-beta.3` targets `main`
- **WHEN** the beta release guard evaluates the pull request before merge
- **THEN** it requires release-candidate validation evidence for the pull request head SHA
- **AND** it fails while that evidence is missing, even though the release-managed version files are unchanged relative to `main`

### Requirement: Prerelease artifacts do not advance stable aliases

The release publishing workflow SHALL accept both stable tags (`vX.Y.Z`) and prerelease tags (`vX.Y.Z-alpha.N`, `vX.Y.Z-beta.N`, `vX.Y.Z-rc.N`). For prerelease tags, Docker publishing SHALL NOT update `latest`, `X`, or `X.Y` aliases, and the GitHub Release SHALL remain marked as a prerelease and not latest. Stable tags SHALL retain existing stable aliases and latest-release behavior.

#### Scenario: beta release publishes beta-only Docker tags

- **GIVEN** release tag `v1.19.0-beta.1`
- **WHEN** the release publishing workflow builds the Docker image
- **THEN** it publishes the exact version tag `1.19.0-beta.1`
- **AND** it MAY publish channel tag `beta`
- **AND** it MUST NOT publish or update `latest`, `1`, or `1.19`

### Requirement: Stable release promotion remains release-please owned

A beta-tested release train SHALL be promoted by merging the normal
release-please stable release PR for the corresponding base version. Stable
promotion SHALL rebuild PyPI, Docker, Helm, and GitHub Release artifacts with
the stable version instead of retagging prerelease artifacts.

Before the stable release PR for `X.Y.Z` is merged, every change in the
release candidate SHALL either be covered by a `vX.Y.Z-beta.N` prerelease
that has been published and deployed to at least one production-scale
environment for a soak of at least 48 hours without new regressions
attributable to the release train, or fall under the safe-delta exception
below. The unsoaked delta — every change not covered by such a soaked
prerelease, whether because no prerelease of the train completed a soak or
because the change landed after the last soaked prerelease — qualifies for
the exception only when it consists solely of documentation, CI, or
release-tooling changes, an urgent security or outage hotfix, or a
combination of these; otherwise the train SHALL soak (again) as a new
prerelease before stable promotion. When promotion relies on the exception,
the exception and its reason SHALL be recorded on the stable release PR
before merge.

When the release train contains Alembic revisions, the maintainer SHALL review
the revisions between the previous stable tag and the release candidate
directly for data-backfill migrations and SHALL estimate their startup impact
against a production-scale dataset before merging the stable release PR.
Generated changelog titles SHALL NOT be treated as sufficient evidence that
the train contains no data backfills.

#### Scenario: beta train is promoted to stable

- **GIVEN** `v1.19.0-beta.2` was published from `main`
- **AND** release-please has prepared the stable release PR for `1.19.0`
- **WHEN** the stable release PR is merged
- **THEN** release-please creates the stable `v1.19.0` release
- **AND** the release publishing workflow publishes stable artifacts for `1.19.0`
- **AND** stable Docker aliases `latest`, `1`, and `1.19` are updated only by the stable release

#### Scenario: stable promotion waits for the beta soak

- **GIVEN** `v1.20.0-beta.1` was published 12 hours ago and is deployed on a
  production-scale environment
- **WHEN** a maintainer considers merging the stable release PR for `1.20.0`
- **THEN** promotion waits until the beta has soaked for at least 48 hours
  without new regressions attributable to the release train

#### Scenario: stable promotion without a soaked beta records an exception

- **GIVEN** no `v1.21.1-beta.N` prerelease has completed a 48-hour soak
- **AND** the entire delta since `v1.21.0` consists of an urgent security
  hotfix and CI changes only
- **WHEN** a maintainer merges the stable release PR for `1.21.1` with the
  exception and its reason recorded on the PR
- **THEN** the promotion is compliant with this requirement

#### Scenario: unrelated unsoaked changes cannot ride a hotfix exception

- **GIVEN** no `v1.22.0-beta.N` prerelease has completed a 48-hour soak
- **AND** the delta since the previous stable release contains an urgent
  hotfix alongside unrelated feature or migration changes
- **WHEN** a maintainer considers promoting `1.22.0` directly to stable
- **THEN** the hotfix exception does not apply to the train
- **AND** the train either soaks as a beta or the hotfix is released
  separately

#### Scenario: changes landing after the soaked beta restart the soak

- **GIVEN** `v1.23.0-beta.1` completed a 48-hour production-scale soak
- **AND** a feature or migration change lands on `main` afterwards, before
  the stable release PR for `1.23.0` is merged
- **WHEN** a maintainer considers promoting `1.23.0` to stable
- **THEN** the post-beta change is part of the unsoaked delta
- **AND** because a feature or migration change is not exception-eligible,
  promotion requires a new soaked prerelease covering it

#### Scenario: data backfills are identified from Alembic revisions

- **GIVEN** the release train adds revisions under `app/db/alembic/versions`
  since the previous stable tag
- **WHEN** the maintainer prepares to merge the stable release PR
- **THEN** they review those revisions directly for data-backfill operations
- **AND** changelog titles alone are not treated as evidence that no backfill
  is present

### Requirement: Stable release promotions guard every release-managed version field

Stable release promotion pull requests SHALL fail CI unless every release-managed version field agrees on the stable version and every field that previously held the prior release train version advances together. The guarded fields SHALL include `pyproject.toml`, `app/__init__.py`, `frontend/package.json`, both Helm chart version fields, and the editable `codex-lb` entry in `uv.lock`.

#### Scenario: release-please stable PR misses uv.lock

- **GIVEN** a beta-tested release train has release-managed files at `1.20.0-beta.3`
- **AND** a release-please stable PR changes `pyproject.toml`, `app/__init__.py`, `frontend/package.json`, and Helm chart versions to `1.20.0`
- **BUT** leaves `uv.lock` at `1.20.0-beta.3`
- **WHEN** CI evaluates the stable release guard
- **THEN** the guard fails before the PR can merge
- **AND** the failure identifies `uv.lock` as a release-managed version field that must be updated

#### Scenario: release-please stable PR updates all release-managed fields

- **GIVEN** a beta-tested release train has release-managed files at `1.20.0-beta.3`
- **WHEN** a release-please stable PR changes all release-managed version fields to `1.20.0`
- **THEN** the stable release guard passes

### Requirement: Failed release publishing withdraws public release metadata

If the Release workflow is triggered by a public GitHub Release event and any required publishing job fails, the workflow SHALL make that GitHub Release draft again before exiting. This prevents `/releases/latest` and dashboard update checks from advertising a version whose PyPI, Docker, or Helm artifacts are incomplete.

#### Scenario: stable release workflow fails before artifacts publish

- **GIVEN** GitHub Release `v1.20.0` was published and triggered the Release workflow
- **AND** the workflow fails before PyPI, Docker, and Helm artifacts are all published
- **WHEN** the failure cleanup job runs
- **THEN** the GitHub Release is changed back to draft
- **AND** the release no longer appears as the public latest release

### Requirement: Fork publication requires successful exact-source checks

The independent fork publisher SHALL require an explicit `vX.Y.Z` or `vX.Y.Z-(alpha|beta|rc).N` tag resolving to the current `main` commit. Before publication it MUST validate the newest main-push run for that exact SHA of CI, release guards, simplicity budgets and Windows startup regression; all four MUST be completed successfully and CI MUST contain a successful `CI Required` aggregate. Missing, pending, cancelled, skipped, failed, stale-SHA or pull-request-only evidence MUST block publication. The publisher MUST recheck source identity and CI after building and before registry login or artifact upload.

#### Scenario: Another SHA has green CI

- **WHEN** the tag's source CI failed but a different commit passed
- **THEN** publication is refused without registry login or artifact upload

#### Scenario: CI is rerun during artifact building

- **WHEN** the initial gate passed but the newest exact-source CI run is pending or failed at the final gate
- **THEN** no artifacts or Docker aliases are published

#### Scenario: Windows evidence is absent or unsuccessful

- **WHEN** the exact-source main-push Windows startup run is absent, pending or unsuccessful
- **THEN** fork publication is refused even if Linux CI passed

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

### Requirement: Upstream release automation has repository-scoped cleanup

Upstream release-please, beta synchronization, beta publishing and upstream artifact publishing SHALL run only in `Soju06/codex-lb`. The upstream Release workflow's failure cleanup MUST also be restricted to that repository. A skipped or cancelled upstream release workflow in a fork MUST NOT withdraw fork release metadata; fork publication SHALL remain governed by the independent fork publisher and its source gates.

#### Scenario: Upstream publisher is cancelled in a fork

- **WHEN** the upstream Release workflow receives a fork release event and an upstream publishing job is cancelled or skipped
- **THEN** upstream cleanup does not edit the fork release

#### Scenario: Upstream publication fails in upstream

- **WHEN** required upstream publishing fails or is cancelled after a public upstream release event
- **THEN** repository-scoped cleanup remains eligible to make that upstream release draft
