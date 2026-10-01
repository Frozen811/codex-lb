## Context

See proposal.md. The upstream publisher is repository-scoped and includes upstream PyPI and Helm credentials; simply enabling it in the fork is inappropriate. CI runs its full matrix on main pushes, whereas PR CI can be area-filtered.

## Goals / Non-Goals

Provide a fail-closed fork release path for GitHub wheel/sdist and linux/amd64 GHCR images. Preserve the upstream release-please, review and soak contracts. No new runtime settings, automatic release creation, deployment, upstream PyPI publication or ARM64 claim.

## Decisions

- Reuse stdlib release version helpers and supported alpha/beta/rc syntax. Historic `hardened.N` tags remain evidence, not accepted input to the repaired publisher. Align current managed files to the existing pyproject `1.25.1`; this is drift repair, not a new released version.
- Require the tag SHA to equal live main. This intentionally blocks delayed old releases rather than risking alias regression; a new candidate is needed when main changes during a build. Validate the latest main-push run per required workflow including CI Required, and repeat immediately before publication.
- Gate in a separate job before the publisher becomes reachable. Checkout immutable SHA in the publisher, build/load a local Docker image, run smoke tests, then publish that same image without rebuilding. Use pinned actions and explicit linux/amd64.
- Package smoke runs outside the checkout in a fresh environment using a temporary SQLite database. Container smoke uses tmpfs with no host production volume. Artifact verification checks archive metadata, dashboard assets and application Python source identity; it never executes downloaded historical artifacts.
- Serialize the entire publisher. Reject existing release assets and exact image tags rather than clobbering on retry. Attach SHA256SUMS and JSON provenance with CI run IDs. Upload packages, publish exact Docker tags, then advance stable aliases and public release metadata.

## Risks / Trade-offs

- GitHub/GHCR updates are not transactional: cleanup withdraws the release, but partial registry uploads can remain. Investigate partial failures before a new candidate; never silently overwrite them.
- Source/CI can change immediately after the final API read: full-workflow serialization and a final recheck narrow the race; this is not a lock on main or CI reruns.
- Existing aliases remain stale until a new valid candidate is published. Do not repair them by relabeling unverified historic builds.
- Local smoke success is not cloud CI evidence. New workflow execution remains unverified until an explicitly published source commit runs in GitHub.

## Migration Plan

Implement and test locally; publish focused reviewed commits when authorized, obtain green main CI, then prepare a coherent beta candidate if runtime changes need soak. Existing releases and running containers are untouched by this implementation.
