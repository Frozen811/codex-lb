## Context

See proposal.md for the five-entry scope. The repository already uses a bounded ordered scan with a per-row delete fence. Failure-detail rewrites can preserve timestamp, count and admission generation, so those three values do not identify the entire observed protection. The current graph supplies the scheduled cleanup caller and existing bridge lifecycle tests; dynamic SQL and framework routing are checked directly in source and runtime tests.

## Goals / Non-Goals

**Goals:** preserve every changed observed retry protection; continue cleanup of independent stale candidates; verify the other four entries against current local code.

**Non-Goals:** migration changes, global quarantine overflow policy, deadline-only probe reclamation, upstream PR acceptance, cloud or production certification.

## Decisions

Add the selected `last_detail` to the existing snapshot and deletion predicate. Use `IS NULL` when the selected value is NULL, and equality otherwise. This preserves SQLite/PostgreSQL/MySQL SQL semantics without requiring a dialect-specific null-safe operator or an artificial version bump. Keep keyset progression after fence misses, which prevents reconsidering the changed row in the same pass while allowing unrelated candidates to be cleaned.

Exercise the repository with real isolated SQLite and inject a committed detail rewrite after candidate selection. Cover both directions of NULL transitions, non-NULL rewrites, unchanged controls and batches with an independent candidate. Compile the actual DELETE for PostgreSQL and MySQL dialects; those checks establish predicate portability, not live backend behavior.

Use existing product-route quarantine completion/recovery regressions and retry lifecycle tests for the four already implemented contracts. Add implementation changes only if their current tests or additional boundary checks expose a scoped defect.

## Risks / Trade-offs

- A changed stale candidate can be removed by a later independent pass if it remains eligible; this is the existing retention policy.
- Detail changes away and back before deletion are indistinguishable from an unchanged snapshot; the contract protects the selected state using existing fields.
- Live PostgreSQL/MySQL, cross-process/provider traffic and upstream policy decisions remain external validation scopes.
- Shared `responses-api-compat` and registry files contain prior dirty work; exact baseline hashes and source-row comparisons preserve those changes.

## Migration Plan

No schema or configuration migration. The additional fence takes effect with the application update; rollback restores the previous deletion predicate.
