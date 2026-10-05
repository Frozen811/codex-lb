## Context

See proposal.md for the selected five rows. Live upstream PR details were read on 2026-10-05; their author claims are not local evidence. Base HEAD is f987d08e69978ee6452c4e5997b11e80a81ba5f2. The preexisting issues-check.md refresh is preserved.

## Goals / Non-Goals

Correct the three reproduced contracts and independently verify the two existing implementations. Preserve account ownership, cleanup, unknown usage, proxy locality and absolute expiry. Hosted clients, cloud CI, released artifacts and deployments are outside this local batch.

## Decisions

- Replace the admin-specific resolver with the existing generic lifetime resolver at the issuance boundary; keep shared locality and provider maximums.
- Normalize lease tokens by the existing maximum reservation estimate, rather than unmeasured credit capacities. Keep transient pressure separate from persisted evidence. Store persisted usage on transient AccountState only; do not add database fields. Use a dedicated relative-availability fallback to preserve other strategies and seeded ties.
- Forward developer message input unchanged and default absent instructions to empty. Continue to normalize system messages, JSON-mode instructions and preserved typed directives. Update existing expectations and golden corpus that encoded the faulty hoist.
- Reuse catalog visibility and redaction policies. Fresh route/formatter checks determine closure. The additional malformed Proxy-Authorization check revealed an actual gap: extend the explicit field matcher while preserving pinned single-quoted Basic repr behavior.

## Risks / Trade-offs

- Longer remote sessions through 30 days follow the existing documented setting; absolute expiry, revocation and TOTP remain covered.
- The existing lease-weight setting changes from invalid mixed units to percentage points. Update its help and stable context without adding settings.
- A synthetic upstream chain proves forwarded wire/history ownership but does not validate vendor persistence. Record that limit explicitly.
- Broad test fixtures may encode developer hoisting; update only assertions affected by the intended contract and run focused transport compatibility coverage.

## Migration Plan

No migration or deployment is performed. Existing cookies keep their embedded lifetime; operators reauthenticate to obtain changed lifetime. Code rollback restores prior normalization/pressure policy without altering stored data.
