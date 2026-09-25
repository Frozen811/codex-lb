# Design: Admit Hard Continuity Owner Serving Its Own Transient Backoff

## Context & Problem Analysis

In codex-lb, request affinity to an account can be established via hard sticky sessions (e.g. durable bridge sessions, explicit conversation turn-state, or required continuity owners).
When selection runs for such requests:
1. `_prepare_sticky_selection_states` or `run_unbound_selection_path` narrows the candidate states list `states` strictly to the account matching `required_account_id` or the pinned owner.
2. If that account has transient errors (`error_count >= 3`), `AccountState` is marked in error backoff.
3. `select_account` partitions the candidates into:
   - fully available accounts (empty because the sole candidate is in backoff)
   - `in_error_backoff` (contains the sole candidate)
   - `hard_blocked_exists` (false because there are no other accounts)
4. The fallback clause:
   ```python
   if allow_backoff_fallback and (
       len(in_error_backoff) > 1
       or (in_error_backoff and hard_blocked_exists)
   ):
   ```
   evaluates to false because `len(in_error_backoff) == 1` and `hard_blocked_exists` is false.
5. Consequently, `select_account` returns `account=None`. The proxy treats this as a hard selection failure (`hard_affinity_saturated`, `continuity_owner_unavailable`), returning HTTP 502 to the client and breaking reconnect loops.

## Technical Design

### 1. `app/core/balancer/logic.py`
Add `hard_owner_pool: bool = False` to `select_account`.
Modify the fallback condition to:
```python
if allow_backoff_fallback and (
    len(in_error_backoff) > 1
    or (in_error_backoff and hard_blocked_exists)
    or (in_error_backoff and hard_owner_pool)
):
```
When `hard_owner_pool=True`, if the sole account in the pool is in error backoff, the fallback activates and admits it.
The account's error counters (`error_count`, `last_error_at`) are NOT cleared; the account simply serves the turn rather than failing the request.

### 2. `app/modules/proxy/_load_balancer/sticky_selection.py`
- In `hard_sticky` selection path: the pool was narrowed to `sticky_existing_account_id`. Pass `hard_owner_pool=True`.
- In `_select_with_stickiness`: accept `hard_owner_pool: bool = False`.
  - When recursing with `required_account_id`: pass `hard_owner_pool=required_account_id is not None`.
  - When calling `_select_account_preferring_budget_safe`: forward `hard_owner_pool`.
- In `finish_selection`:
  - `_choose_from` forwards `hard_owner_pool=hard_owner_pool`.
  - Seed-preference check: `allow_backoff_fallback=hard_owner_pool`, `hard_owner_pool=hard_owner_pool`.
  - Pinned-owner retention checks (both initial and budget threshold check): `allow_backoff_fallback=hard_owner_pool`, `hard_owner_pool=hard_owner_pool`.
  - `pool_best` check: `hard_owner_pool=hard_owner_pool`.
- In `_select_account_preferring_budget_safe`: accept `hard_owner_pool: bool = False` and pass it to all internal `select_account` invocations.

### 3. `app/modules/proxy/_load_balancer/unbound_selection.py`
- In `_select_from(candidates)`: pass `hard_owner_pool=required_account_id is not None` to `_select_account_preferring_budget_safe`.

### 4. `app/modules/proxy/load_balancer.py`
- Forward `hard_owner_pool: bool = False` in `_select_with_stickiness`.

## Failure Mode & Invariant Analysis

- **Persisted Unavailability**: If the hard owner is `PAUSED`, `DEACTIVATED`, `RATE_LIMITED`, `QUOTA_EXCEEDED`, or has expired reauth, it is excluded before `in_error_backoff` is evaluated. It will still fail closed.
- **Multi-Account Pools**: If `hard_owner_pool=True` is somehow passed with multiple accounts, the existing condition `len(in_error_backoff) > 1` or selecting healthy siblings takes precedence. A healthy account will always be chosen over a backed-off account.
- **Soft Affinity**: Soft sticky sessions (e.g. prompt caching) do NOT narrow to a single account and do NOT pass `hard_owner_pool=True`. They can freely rebind to a healthy sibling.
