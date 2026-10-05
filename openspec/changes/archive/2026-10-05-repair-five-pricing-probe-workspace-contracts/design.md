## Context

See proposal.md for scope. Existing code already owns detached append tasks and fences settlement phases, uses disjoint cache-write accounting, and names failover walk endings. Upstream patches need adaptation to those newer contracts.

## Goals / Non-Goals

Preserve ownership, accounting and zero-config startup behavior. Do not add application configuration, import unrelated dependencies, alter shutdown policy, or claim published/cloud/provider verification.

## Decisions

- Add explicit Ultrafast price fields for all four token categories and context groups; use Decimal products for integer monetary settlement. Preserve genuine fractional truncation.
- Preserve existing price merge validation and offline precedence. Bundle the documented Astra rates, including cache writes.
- Stop cancelling append tasks at the delivery bound; retain the existing task set, done callback, shutdown ownership, terminal phase and attempt fences.
- Extend the shared exact native identity sets, including slash-delimited gateway User-Agent prefixes. Do not add an operator setting.
- Add account_unavailable to the existing failover policy and benching classification. Adapt failover_outcome rather than replacing it with the older decision function. Defer keyed workspace health through existing settlement paths only.
- Render startup timing from validated chart values; reject null objects/fields, noninteger values, and successThreshold other than one.

## Risks / Trade-offs

- Late writes can outlive delivery: settlement phase prevents replay and shutdown continues to own cleanup.
- Cost arithmetic must preserve cache-write partitioning: regression coverage includes mixed categories and exact/fractional monetary boundaries.
- Native classification changes routing behavior: test HTTP and both WebSocket header builders, with lookalike negative controls.
- Workspace health is permanent: classify only the exact upstream code; test bare 402 and sibling records.
- Chart rendering is local evidence: cluster/runtime/cloud validation is outside this source batch.

## Migration Plan

No schema or data migration. Keep all existing prices and probe defaults except the newly supported tier. No production deployment is performed.

