## Context

See proposal.md for the five selected source records. The fork already has durable bridge prefix fingerprints, pending-call manifests, one-shot recovery fences, persisted quota holds and guarded owner retirement. These remain the authority for recovery.

## Goals / Non-Goals

**Goals:** Preserve context and account ownership on reconnect; provide testable client setup and local evidence for all selected records.

**Non-Goals:** Import upstream branches wholesale, calibrate plan capacities, change the public Realtime API, transfer opaque context across accounts, publish or deploy.

## Decisions

- Track the empty prewarm's client-visible response ID and input prefix separately from completed generated turns. A delta cannot prove that removing this anchor preserves context.
- Add an explicit default-off same-owner agent flag to the existing context predicates. Strictly validate agent shape, remove only trailing valid agent messages from the proof view, and preserve dispatch input. Account-neutral predicates continue rejecting these items.
- A durable full-resend proof pins the original account even after anchor removal; owner retirement and selection fallback cannot override that pin.
- Treat the named policy conflict as a candidate for the existing guarded repository retirement. Availability, deadline, file pin and one-attempt conditions remain unchanged.
- Existing quota reset behavior is verified at persisted repository and API boundaries; no obsolete recovery patch is needed.

## Risks / Trade-offs

- Experimental client settings can change: document their provenance and require installed-client support, without claiming a live voice test.
- Overbroad replay admission could move opaque data: test malformed messages, missing manifests/calls/outputs, quarantine, unavailable owner, visible output and missing operation fences.
- Policy-only exclusion can hide a healthy owner: test healthy and near-reset owners remain bound.

## Migration Plan

No schema migration. Changes are local source fixes with existing defaults; rollback is the reviewed source diff.
