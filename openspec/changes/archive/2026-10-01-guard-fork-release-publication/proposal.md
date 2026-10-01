## Why

The fork can publish Docker images from failing source CI, and its public release tag, package version, runtime version and Docker aliases disagree. Publication must establish exact source and artifact identity before advertising an update.

## What Changes

- Replace the fork's ungated Docker workflow with a source gate and locally validated package/image publication.
- Require an explicit supported release tag, current main SHA, successful current source workflows and coherent managed versions.
- Publish exact version tags; stable aliases advance only for stable releases after smoke checks and a final source recheck.
- Withdraw incomplete GitHub releases, preserve existing assets on retries, and record checksums/source provenance.
- Repair existing managed version drift without creating or publishing a new release.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `release-management`: independent fork publishing contract, source CI gate, artifact parity and failure behavior.

## Impact

Fork Docker workflow, stdlib release scripts, focused regression tests, version files and release-management context. No upstream PyPI or Helm registry publishing, application settings, database changes or public tag rewrites.
