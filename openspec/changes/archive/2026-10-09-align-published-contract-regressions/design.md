## Context

See proposal.md. CI #90 completed with 26 successful jobs and nine failed jobs, comprising six test jobs and three aggregate gates. Windows startup, PostgreSQL, frontend, Rust, Docker/Trivy, Helm, and Nix passed. Local reproduction confirms all four underlying test failures.

## Goals / Non-Goals

Verify existing route and transport contracts using accurate premises and explicit assertions. Application behavior, public contracts, settings, and database schemas remain outside this test-only change.

## Decisions

- Extend the alpha-search fake with explicit `body_session_id` and `allow_cross_account_retry` arguments and assert their ordinary-control values. This checks the complete call contract rather than swallowing unknown keywords.
- Add all four plugin route aliases to the fail-closed inventory and exercise canonical/slash aliases in existing capability-denial cases. The exact inventory equality and disjoint-policy check remain intact.
- Keep original JSON text assertions for raw HTTP SSE. For auto transport, assert the WebSocket path and its canonical SSE JSON, as permitted by the existing bridge relay requirement. Keep all semantic usage, Unicode, delta, timing, cost, reservation and report assertions.
- Add an unresolved `function_call_output` to the coded-429 owner-bound fixture. The published ciphertext-only exception permits failover; an output whose call exists only in the owner's context remains independently account-bound. Existing routing-ownership tests cover the ciphertext-only positive case. An explicit response anchor instead enters bridge continuation before the intended low-level error path, so it is unsuitable for this fixture.

## Risks / Trade-offs

An imprecise test update could hide a regression. Preserve strict call arguments, exact route coverage, HTTP bytes, WebSocket framing, semantic payloads, and the hard-owner no-retry assertions. Re-run all changed integration files and the focused burst/routing controls, then publish and require the complete CI matrix on the new SHA.
