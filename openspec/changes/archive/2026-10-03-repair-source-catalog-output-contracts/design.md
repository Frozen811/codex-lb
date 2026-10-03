## Context

See proposal.md for the audit scope. Catalog projection already stores source
instructions on the typed registry field. Tool filtering already derives
namespace support from a nonblank `multi_agent_version`; the main spec still
omits that declaration. Output-budget projection is shared by list entries,
individual retrieval, metadata and capability aliases.

## Goals / Non-Goals

Verify the observable catalog-to-request contract and repair invalid budget
precedence. Preserve raw native catalog metadata, generation behavior, source
identity, accounting and current operator defaults. Public release and cloud
certification are separate audit scopes.

## Decisions

- Validate budgets at the shared compatibility projection: only a positive
  integer excluding booleans is a usable count. Reuse existing slug fallbacks;
  unknown slugs retain null when their raw count is invalid. Do not coerce
  strings/floats or mutate registry/native metadata.
- Exercise dashboard create/update, stored metadata readback, native catalogs
  and real loopback HTTP forwarding. This verifies the product path instead
  of duplicating a converter-only assertion.
- Preserve declared namespaces for future nonblank versions. Bare function
  choices remain supported; a function choice naming a dropped namespace must
  be pruned, including inside `allowed_tools`. Existing tool-type filtering
  supplies the namespace-presence evidence without a new capability setting.
- Keep rationale/examples in context documents and synchronize full modified
  requirement blocks before archive.

## Risks / Trade-offs

- Malformed positive-count assumptions in imported metadata -> route tests
  cover booleans, nonpositive values, missing fields and valid precedence.
- Clients can cache old catalogs -> document explicit catalog refresh.
- Loopback stubs do not certify hosted providers or released artifacts -> keep
  those residuals explicit in verification and the audit registry.

## Migration Plan

No schema or configuration change. Rollback restores the shared budget/choice
projection; stored source metadata is unchanged.
