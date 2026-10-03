## Context

See proposal.md. All three route families exist in HEAD. Search uses the shared control dispatcher, and single-model retrieval already uses the catalog visibility policy. Native notes are opaque control payloads with existing thread/session affinity; tests must exercise those policies rather than replacing the service.

## Goals / Non-Goals

Goals: direct slash-equivalent dispatch, individual-model list parity, stronger HTTP evidence for all ten history/notes operations.
Non-goals: account-pool history recovery, new ownership policy, live credentialed upstream traffic, release publication, settings or schema changes.

## Decisions

- Register hidden slash routes on the existing handlers. This avoids redirect round trips and resending authenticated POST bodies. Do not globally normalize arbitrary routes.
- Register the single-model slash route before the existing path-converter route, so only the delimiter is removed and nested model IDs remain intact. Do not strip arbitrary characters from model IDs in the catalog resolver.
- Exercise real account imports, API-key scopes and control service; replace only the upstream transport in native-route regressions. Capture body bytes, repeated query parameters and allowed encryption headers.
- Preserve existing native Content-Type replacement/compression handling and validate it with its transport regressions.

## Risks / Trade-offs

- Greedy model path conversion could shadow the slash route -> explicit route ordering and nested-ID cases.
- Synthetic upstream fixtures do not prove hosted search or private notes data recovery -> keep live incidents/public artifact scope explicit in the registry.
- Existing dirty checkout -> narrow additive edits; no commit, push or release.
