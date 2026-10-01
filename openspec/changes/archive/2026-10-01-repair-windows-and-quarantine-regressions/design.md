## Context

The batch covers audit findings F-005, F-011 and F-008. Existing edits from previous batches remain separate. The quarantine file passes in isolation on this Windows host; CI evidence must be explained through a deterministic failing path.

## Goals / Non-Goals

Repair the three findings with focused regression evidence. No release, source publication, new configuration, schema changes or claim of Windows transport parity.

## Decisions

- Use Path.as_posix for architecture diagnostics, preserving relative/absolute identity.
- Enable the Windows workflow on all source-validation events without path filters, retaining a stable check context.
- Reuse the existing isolated release smoke for a fresh wheel installed outside the checkout. Build dashboard with the pinned Bun version and install with uv without shared-cache hardlinks.
- Add Windows workflow to the fork's exact-source release prerequisite list. Manual runs remain diagnostic evidence, not substitutes for main-push evidence.
- Quarantine reproduction shows the helper reported an aggregate adopted deadline as the local evidence deadline. Correct the helper to return local poison/suppressed weaker expiry; add both durable-first and local-first ordering at the actual Responses route. Production quarantine logic already subtracts adopted evidence correctly and requires no behavior change.

## Risks / Trade-offs

Windows builds add CI time. A local smoke proves only the local machine/artifact; edited workflow cloud evidence remains unavailable until source publication. Existing-main manual dispatch may provide baseline evidence only.
