## Context

See proposal.md. Existing catalog and native control routes cover most selected behavior, but body-session ownership is missing and bootstrap Astra is absent. The graph identifies api.py -> codex_control.py -> affinity.py and existing shared selection/failover helpers.

## Goals / Non-Goals

Repair exactly five registry scopes; preserve opaque native payloads and existing ordinary Responses locality. No pooled history fan-out, ciphertext envelope, schema, settings or client-version upgrades.

## Decisions

- Add a hard history_session affinity in a header-impossible hashed namespace. Seed it from the native session's soft process owner and retain header compatibility when body identity is absent.
- Parse only supported native POST bodies at API ingress. Preserve original bytes rather than serializing the parsed object.
- Thread retry permission through existing control orchestration. Pass the selected account as strict owner to refresh and retry helpers, and prevent the manual 401 cross-account branch.
- Reuse existing bootstrap and model-label helpers for Astra, using the captured upstream catalog instead of inventing metadata or replacing the pricing snapshot.
- Register explicit plugin backend-api and slash routes, preserving query and pool-credential behavior.
- Verify Spark registry export/import and published discovery examples without altering already working product behavior.

## Risks / Trade-offs

Native history and notes remain account-local after inference rotation. Real client/provider and multi-backend behavior require separate validation. Captured Astra metadata is a startup fallback; live metadata supersedes it.
