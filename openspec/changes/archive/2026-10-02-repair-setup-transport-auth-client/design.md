## Context

See proposal.md. Outermost middleware captures socket peer then projects client/scheme; dashboard identity sanitizer/resolver currently read the projected client. This breaks valid trusted-header auth and can grant proxy provenance to a spoofed projected address. Existing locality/firewall helpers already use captured raw peers. OAuth callback bind OSError is swallowed to keep browser/manual recovery but the initialized AppRunner is discarded without cleanup. Client guide includes an unmatched conflict marker and example usage base disagreement.

## Goals / Non-Goals

Goals: fix concrete provenance/cleanup defects, validate transport/auth through observable routes, and verify installed Codex against isolated synthetic upstream.

Non-goals: production traffic, real ChatGPT login, model/pricing/catalog changes, provider feature redesign, publication or user configuration edits.

## Decisions

- Use the existing raw_socket_peer_host helper in both identity consumers; fail closed without capture. Preserve projected caller for firewall/locality and scheme for CSRF/cookies. No speculative client fallback.
- Callback server owns initialization cleanup even on cancellation; its caller logs only bind metadata and preserves pending manual flow. Keep API schema and OAuth fallback semantics unchanged.
- Rehearse with disposable Docker source runtime, local TLS certificate and stub Responses upstream. Actual Codex 0.159.3 receives only synthetic data under isolated CODEX_HOME. Route and quota/Pause assertions must observe account selection and upstream calls, not merely process exit.
- Separate CLI API-key and ChatGPT-auth provider paths based on official auth guidance and observed selected-client behavior; preserve existing advanced restricted-provider contracts. Capture version-specific discrepancies explicitly.

## Risks / Trade-offs

- Hand-built unit Request scopes need captured provenance to represent a server-observed peer; route tests exercise real middleware ordering.
- Synthetic token exchange/generation cannot certify OpenAI login or account entitlement. Report that limitation rather than silently claiming live upstream success.
- TLS fixture cert is test-only; operator guidance uses their own trusted certificate. Tests retain certificate verification.
