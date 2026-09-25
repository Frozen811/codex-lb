## Context

In the OpenAI Responses API, continuity states (`previous_response_id` and turn-states) are intrinsically account-scoped on upstream infrastructure. A response created by account A cannot be resumed or referenced by account B.

Previously, `compact.py` and `streaming/retry.py` attempted to guess whether an account owned a `previous_response_id` when the database lookup missed: if `len(selection_inputs.accounts) == 1` for the requested model, the proxy assumed that the sole surviving account was the owner. Similarly, the WebSocket session loop did not mark the preferred account as mandatory if the owner lookup missed, leading to arbitrary pool dispatch or improper socket reuse. Furthermore, model source routing only inspected `previous_response_id`, ignoring turn-state continuity, which allowed model sources to override active subscription sessions.

## Goals / Non-Goals

**Goals:**
- Eliminate all single-account availability heuristics for continuation ownership: a missing recorded owner for `previous_response_id` must fail closed with HTTP 502 `previous_response_owner_unavailable` across all transports (HTTP bridge, direct HTTP streaming, compact, and WebSocket).
- In direct WebSocket routing, ensure a missing `previous_response_id` owner lookup fails closed immediately at both connect-time and socket-reuse rather than falling back to an unpinned account.
- In model-source routing (`_select_responses_model_source_with_continuity`), resolve continuity ownership for both `previous_response_id` and turn-state headers (`x-codex-turn-state` / `turn-state`). When a subscription owner is proven, suppress the model source.
- In WebSocket source guards, ensure that an established preferred owner account prevents spurious `model_source_requires_http_transport` rejections.

**Non-Goals:**
- Allowing unanchored cross-account migration when the full history is not verified or when the client explicitly requested an anchored turn.
- Modifying the underlying `request_logs` indexing or schema.

## Decisions

### 1. Fail closed immediately on missing `previous_response_id` owner
In `app/modules/proxy/_service/compact.py` and `app/modules/proxy/_service/streaming/retry.py`, remove the `len(selection_inputs.accounts) != 1` branches. If `_resolve_websocket_previous_response_owner` returns `None`, immediately record `_record_continuity_fail_closed` and raise/yield HTTP 502 `previous_response_owner_unavailable`.

### 2. Guard WebSocket connect and socket reuse
In `app/modules/proxy/_service/websocket/mixin.py`:
- At connect time (line 2185), if `previous_response_id` is present and `_resolve_websocket_previous_response_owner` returns `None`, raise `ProxyResponseError(502, ...)` to fail closed before account selection.
- At socket reuse (line 1918), if `previous_response_id` is present and `_resolve_websocket_previous_response_owner` returns `None`, raise `ProxyResponseError(502, ...)` to prevent sending unproven continuation IDs to the currently attached upstream.

### 3. Check turn-state continuity in model source routing
In `_select_responses_model_source_with_continuity`:
- If `payload.previous_response_id` is not present, inspect `request.headers` for `x-codex-turn-state` or `turn-state`.
- Query `_resolve_compact_turn_state_owner(turn_state, api_key=api_key, fail_on_missing=False)`.
- If an owner is resolved, set `continuity_suppressed = True` to preserve subscription routing.

### 4. Align WebSocket source guards with preferred accounts
In `websocket/mixin.py` (lines 1958 and 3708):
- Check `request_state.previous_response_owner_account_id is None and request_state.preferred_account_id is None` before executing `responses_model_is_source_owned`.

## Risks / Trade-offs

- *Risk*: A client that sends an arbitrary unrecorded `previous_response_id` against a single-account setup will now receive `previous_response_owner_unavailable` rather than being speculatively served by the only account.
- *Mitigation*: This is the intended behavior and contract of the OpenAI Responses API. Sending an unknown `previous_response_id` to an account that did not generate it results in upstream errors, conversation corruption, and cross-account context leakage.

## Migration Plan

No database migration, setting changes, or client configuration updates are required. Deploy as a proxy logic correction.

## Open Questions

None.
