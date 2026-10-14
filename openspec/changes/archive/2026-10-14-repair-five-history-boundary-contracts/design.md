## Context

See proposal.md. Existing source claims and helper tests do not establish route behavior. The live upstream issue comments distinguish portable input from opaque compaction and reject broad transcript omission. The checkout contains previous dirty work, preserved through file hashes and initial copies.

## Goals / Non-Goals

Goals: consume call occurrences without changing payload bytes; use the existing sticky-thread opt-in to defer pressure reallocation; verify externally rendered errors, bounded recovery and ownership.

Non-goals: changing default prompt-cache policy, adding a new environment field or dashboard UI control, reproducing an entire deployed relay chain or publishing work.

## Decisions

- Consume one pending call occurrence per matching output, separated by protocol. Reused IDs with repeated call/output pairs remain valid; repeated outputs without new calls retain continuity.
- A non-null dashboard timing column defaults to `immediate`, including historical rows. The validated settings API permits `after_compaction`. Resolve timing with the existing frozen routing snapshot; default mode preserves all prior behavior. In deferred mode ordinary soft affinity passes reallocation false; explicit compact and safe recovery pass true. No settings read occurs inside selection locks.
- Keep artifact slimming item-preserving. Verify files, tool identities, latest suffix and framing; still oversized requests fail locally.
- Exercise real application routes, SQLite accounts, selection and settlement, replacing only the provider transport. Status/event quota cases include plain images, retained reasoning and compaction. The existing narrowed ciphertext-only rejection exception forwards ciphertext unchanged after checking the remaining request; explicit owners, opaque resources and ambiguous failures retain their existing boundaries.

## Migration Plan

Append revision `20261014_000000_add_sticky_reallocation_timing` to the current fork head. Use a bounded VARCHAR(32), a non-null `immediate` server default and a downgrade that removes only this field. Verify historical rows, schema drift and upgrade/downgrade/upgrade on disposable SQLite, PostgreSQL and MySQL. Keep `immediate` unless an operator chooses the new mode; reverting the setting requires no migration.

## Risks / Trade-offs

- Deferred pressure can retain a nearly exhausted account longer: explicit exhaustion and safe retry remain available.
- Incomplete retained history cannot be transferred safely: preserve the original quota error rather than lose context.
- Tests use fake provider transports: live Desktop/provider and distributed rollout evidence stay separate.
