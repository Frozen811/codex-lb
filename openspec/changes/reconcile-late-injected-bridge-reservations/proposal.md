# Proposal: Reconcile Reservations After Late HTTP-Bridge Anchor Injection

## Why
When a client sends an unanchored (self-contained) request to the HTTP bridge, API-key admission computes a bounded reservation based on the self-contained payload shape (e.g. a small prompt only reserving ~50 tokens).
Later, during bridge processing, the request can advance a durable hard-turn operation or attach a session-level anchor, injecting `previous_response_id` into the request before dispatch.
Because an anchored request relies on opaque upstream context, its reservation budget should be the conservative input default (`API_KEY_USAGE_RESERVATION_DEFAULT_INPUT_TOKENS` = 8192 tokens).
Without reconciling the reservation before the anchored frame is dispatched, the in-flight reservation severely under-reserves against the API-key quota, permitting subsequent requests to over-consume the quota during the request's execution, and desynchronizing the reservation ledger from the actual request semantics.

## What Changes
- Add `reconcile_usage_reservation` to `ApiKeyService` and `update_reservation_item_reserved_delta` to `ApiKeyRepository`.
- When the HTTP bridge injects `previous_response_id` (advancing a durable hard-turn operation or session anchor), reconcile the existing API-key reservation to the opaque-context budget before upstream dispatch.
- If reconciling the reservation exceeds configured API-key limits, reject the request with HTTP 429 (`rate_limit_exceeded`) as a local pre-dispatch refusal.

## Capabilities

### Modified Capabilities
- `api-keys`: API-key usage reservations MUST reconcile in-flight reserved deltas when an unanchored request transitions to an anchored request with opaque upstream context prior to dispatch.
