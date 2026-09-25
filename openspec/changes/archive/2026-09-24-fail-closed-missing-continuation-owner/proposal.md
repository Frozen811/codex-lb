## Why

A continuation (`previous_response_id` or `turn_state`) identifies account-scoped upstream state on the OpenAI Responses API. When continuity owner evidence is missing or conflicts, the proxy must fail closed rather than guessing or misattributing ownership.

Three defects currently violate this invariant:

1. **Model-filtered single-account heuristic**: In `compact.py` and `streaming/retry.py`, when a `previous_response_id` owner lookup misses, the proxy loads `selection_inputs` for `model` and checks `if len(selection_inputs.accounts) != 1:`. If exactly one account in the pool currently supports the requested model (Account A), the proxy does not fail closed; instead, it treats Account A as the "only possible owner" and forwards the continuation to it. Being available for routing does not prove ownership: the previous response could belong to Account B (which may currently lack quota, be offline, or not support the model). In `streaming/retry.py`, `_load_selection_inputs` also passed `account_ids=None`, ignoring API key assignment scopes.
2. **WebSocket arbitrary fallback on missing owner**: In `websocket/mixin.py`, when a WebSocket request arrives with `previous_response_id` and the owner lookup misses, `preferred_account_id` remains `None`. `_websocket_request_requires_preferred_account` returns `False`, allowing connect-time selection to dispatch to an arbitrary available account from the pool, or allowing socket reuse to send the continuation to whatever account the socket is currently connected to.
3. **Model source precedence over known subscription continuity**: In `_select_responses_model_source_with_continuity` (`app/modules/proxy/api.py`), model source suppression only checks `previous_response_id`. Continuations carrying `turn_state` (such as `x-codex-turn-state` headers) without `previous_response_id` do not resolve turn-state ownership before selecting a model source. A configured model source can hijack an active conversation belonging to a subscription account. Similarly, WebSocket source guards in `websocket/mixin.py` checked only `previous_response_owner_account_id is None`, ignoring `preferred_account_id` established by turn-state or bridge ownership, erroneously emitting `model_source_requires_http_transport`.

## What Changes

- **Eliminate single-account owner guessing**: Remove the `len(selection_inputs.accounts) != 1` heuristic in `compact.py` and `streaming/retry.py`. When a continuation carries `previous_response_id` and owner resolution misses, fail closed immediately with HTTP 502 `previous_response_owner_unavailable` and record continuity fail-closed telemetry.
- **Fail closed in WebSocket on missing continuation owner**: In `websocket/mixin.py`, when `previous_response_id` is present but `_resolve_websocket_previous_response_owner` returns `None`, fail closed with `previous_response_owner_unavailable` on both connect-time and socket reuse.
- **Respect turn-state continuity in model source routing**: In `_select_responses_model_source_with_continuity`, resolve subscription ownership from both `previous_response_id` and turn-state headers (`x-codex-turn-state` / `turn-state`). When a subscription owner is proven, suppress the model source.
- **Protect known subscription owners in WebSocket source guards**: In `websocket/mixin.py` lines 1958 and 3708, check that neither `previous_response_owner_account_id` nor `preferred_account_id` is set before applying `responses_model_is_source_owned`, preventing spurious `model_source_requires_http_transport` rejections for active subscription sessions.

## Capabilities

### Modified Capabilities

- `responses-api-compat`: Mandate fail-closed handling for missing `previous_response_id` owners across all transports and ensure known subscription continuity owners take precedence over configured model sources.
- `account-routing`: Disallow heuristics that infer account ownership from candidate pool counts or model support.

## Impact

- Closes Issue #2274.
- Prevents leakage of private continuation context and unresolvable upstream errors caused by sending continuations to the wrong account.
- Preserves subscription session continuity when an API key has both subscription accounts and model sources configured.
- Zero changes to database schema, settings, or CLI surface.
