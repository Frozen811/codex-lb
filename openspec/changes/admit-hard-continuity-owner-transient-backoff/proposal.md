# Change: Admit Hard Continuity Owner Serving Its Own Transient Backoff

## Why

A hard continuity owner is selected from a candidate pool that the caller has already narrowed to that single account. When that owner is serving a bounded transient error backoff (`error_count >= ERROR_BACKOFF_THRESHOLD`), the candidate pool goes empty and the turn fails as `hard_affinity_saturated` or `continuity_owner_unavailable` — even though the account is `ACTIVE`, is serving other requests normally, and would exit the backoff in seconds.

The backoff fallback in `select_account` exists for this purpose, but both of its existing activation conditions are unreachable in a pool of one:
```python
if allow_backoff_fallback and (
    len(in_error_backoff) > 1                      # cannot hold in a pool of one
    or (in_error_backoff and hard_blocked_exists)  # inspects other accounts; there are none
):
```
Both conditions ask "is this pool empty for a reason other than the backoff?" by inspecting *other* accounts. A narrowed owner pool has no other accounts, making both conditions evaluate to false.

This violates two established rules:
1. `openspec/specs/sticky-session-operations/context.md`: *"Local caps, retry exclusions, transient runtime health, and budget pressure never authorize legacy hard-owner abandonment."*
2. `app/modules/proxy/_load_balancer/overload_backoff.py`: the isolation window drops an account *"only while at least one other candidate remains, so the window can never empty the pool"*, and hard continuity owners are *"never moved by this module"*.

## What Changes

- Add a `hard_owner_pool: bool = False` flag to `select_account` in `app/core/balancer/logic.py`. When set, if `in_error_backoff` contains the sole candidate and `allow_backoff_fallback` is enabled, the fallback admits that backed-off candidate instead of failing closed.
- Thread `hard_owner_pool` through:
  - `app/modules/proxy/_load_balancer/sticky_selection.py`:
    - `hard_sticky` branch passes `hard_owner_pool=True`.
    - `_select_with_stickiness` passes `hard_owner_pool=required_account_id is not None` when recursing or invoking `_select_account_preferring_budget_safe`.
    - Seed-preference and pinned-owner retention calls pass `allow_backoff_fallback=hard_owner_pool` and `hard_owner_pool=hard_owner_pool`.
    - `_select_account_preferring_budget_safe` accepts `hard_owner_pool` and forwards it to `select_account`.
  - `app/modules/proxy/_load_balancer/unbound_selection.py`:
    - `_select_from` passes `hard_owner_pool=required_account_id is not None`.
  - `app/modules/proxy/load_balancer.py`:
    - `_select_with_stickiness` passes `hard_owner_pool=hard_owner_pool`.
- Persisted unavailability (`PAUSED`, `DEACTIVATED`, `RATE_LIMITED`, `QUOTA_EXCEEDED`, expired reauth) is filtered prior to the fallback and continues to fail closed. Multi-account pools remain unaffected.

## Impact

- Zero `hard_affinity_saturated` and `continuity_owner_unavailable` drops during upstream capacity or transient incident spikes on pinned sessions.
- Pinned sessions remain on their legitimate owner even when that owner has accumulated 3+ transient errors and is in bounded backoff.
