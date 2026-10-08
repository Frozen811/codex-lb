## Context

See proposal.md for the exact five source records. The current fork contains owner SSE framing and model-source collaboration metadata fixes, but omits tool-search pairs from replay and tracks only synchronous calls. Request validation rewrites strings and instruction messages before bridge input classification. Previous dirty packages are backed up outside the repository.

## Goals / Non-Goals

Goals: preserve history and typed tool identity across both Responses transports; verify existing internal owner classification with authenticated body evidence; keep existing reservations, ownership and fail-closed recovery gates.

Non-goals: new settings, migrations, unconditional namespace forwarding, wider top-level replay tool allowlists, live provider certification, publication or deployment.

## Decisions

- Adapt the reviewed, focused upstream implementations to the current fork rather than transplanting an upstream branch. Read runtime hunks, map callers, and add the upstream regression paths with independent fork controls.
- Tool-search outputs carry loaded function/custom declarations, optionally one namespace deep. Validate those declarations before bypassing schema-reference traversal; reject server execution, hosted/MCP tools, unknown fields and malformed loading flags.
- Async applies only to boolean function/custom markers. Preserve validation evidence for already settled pairs and durable prefixes. Track delayed typed outputs separately, clear state on account/anchor changes, and never use an async marker to evade the durable synchronous manifest.
- Keep the fork's conservative full-resend classifier: strings and singleton arrays remain deltas, and longer arrays qualify only with self-contained tool-call/output identities. The upstream size heuristic is superseded here and its new classifier negotiation is unnecessary. Verify normalization and authenticated existing V2 forwarding preserve classification, tools omission and body-tamper rejection.
- Existing SSE and source namespace behavior get focused client/route regressions. No new runtime settings are required.

## Risks / Trade-offs

- A weaker upstream classifier could discard history: do not replace the fork's existing self-contained predicate with the older size heuristic.
- Owner forwarding can alter validation semantics: exercise public routes and signed body roundtrips, preserving existing V2 codec and omission rules.
- Relaxed async ordering can widen replay accidentally: preserve full validation, typed ID matching, assistant completion boundaries and account ownership; test malformed markers and persisted manifest disagreements.
- Large existing proxy test modules contain unrelated cases: run focused subsystem selections and retain external/platform residuals.
