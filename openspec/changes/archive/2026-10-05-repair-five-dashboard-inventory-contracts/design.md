## Context

See proposal.md for the five selected source records. Existing Accounts list and APIs page already provide filters, permission checks and detail actions. The dashboard catalog currently uses an untyped mapping and returns early on an empty Responses registry. Three locale files and api-keys specs contain earlier uncommitted fixes that must be preserved.

## Goals / Non-Goals

Adapt focused upstream UI slices to the current checkout, verify real rendered controls and dashboard/API allowlist paths, and record synthetic desktop/mobile pixels. Provider execution, cloud merge gates and broad upstream PR #2065 remain outside this local repair batch.

## Decisions

- Reuse the donut's capacity mode by adding a distribution presentation, rather than introducing another chart framework. Derive distributions before list filters.
- Reuse existing key usage summaries and permissions. Centralize recorded usage interpretation so overview counts and unused filtering cannot disagree. Keep detail as the zero-config default; tolerate localStorage failures.
- Share image identifiers with request validation and use typed dashboard response models. Images are adapter entries; the native Responses catalog remains unchanged. Filter image-only models at the Automations consumer.
- Use a single minute timer for the expiry marker, cleaned up on visibility changes and unmount. Evaluate the current time when settings become visible again; no new requests.
- Extend existing deterministic account sorting. Unknown quota values remain last even in descending order; zero is not missing.

## Risks / Trade-offs

- Minute polling can delay a warning boundary by less than a minute; tests use a fixed clock and exercise cleanup and visibility transitions.
- Upstream patches may contain stale contexts; inspect current files, apply only selected concerns and run local regression tests instead of accepting author claims.
- UI layout can overflow on mobile; inspect fresh 1440px/390px captures and verify scroll width.

## Migration Plan

No database migration or new configuration. Rollback consists of reverting only this batch's additions. SHA256 baseline snapshots outside the repository support verification of existing dirty work.
