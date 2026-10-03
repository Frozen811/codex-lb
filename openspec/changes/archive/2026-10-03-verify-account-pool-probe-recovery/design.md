## Context

See proposal.md for the three registry items. The routing cache reads status, reason, encrypted token, and deletion markers in one serialized projection. It already excludes proven access rejection for routing, while metric availability consults only token expiry. Force Probe already snapshots ORM rows before rollback/close and fences settlement with a local health version. Weekly-primary normalization is shared by selection and probing.

## Goals / Non-Goals

Keep one account read per metrics scrape and the existing metric labels. Verify real database and API paths. Keep routing, Force Probe response fields, health thresholds, independent cooldowns, and sticky ownership unchanged. Expose quota-exceeded Resume through the existing callback and API.

## Decisions

- Use the existing shared credential-availability predicate for the metrics count; a second reason list would drift from routing.
- Preserve status inventory even when an account's credentials are unavailable. `reauth_required` is useful inventory independently of availability.
- Exercise weekly-only usage through the probe and response routes with a synthetic upstream, committed rows, and real repository cleanup. Do not infer runtime certification from helper-only tests.
- Add `quota_exceeded` to the existing Resume eligibility predicate; reuse the current permission, busy/read-only checks, and reactivation mutation. No new API or setting is needed.

## Risks / Trade-offs

- Optional Prometheus can silently skip exporter tests: install the existing locked metrics extra and require those tests to execute.
- Baseline availability does not predict per-request quota, affinity, or concurrency admission: retain the documented scope.
- Upstream and published artifacts are outside local verification: record those residuals explicitly.

## Migration Plan

No migration or deployment is required. Synchronize the owning spec/context after focused regression and static checks, record verification, and archive only the completed local change.
