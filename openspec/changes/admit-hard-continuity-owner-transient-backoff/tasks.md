# Tasks

## 1. Specification & Artifacts

- [x] 1.1 Create `openspec/changes/admit-hard-continuity-owner-transient-backoff/proposal.md`.
- [x] 1.2 Create `openspec/changes/admit-hard-continuity-owner-transient-backoff/design.md`.
- [x] 1.3 Create `openspec/changes/admit-hard-continuity-owner-transient-backoff/tasks.md`.
- [x] 1.4 Create `openspec/changes/admit-hard-continuity-owner-transient-backoff/specs/sticky-session-operations/spec.md` delta spec.

## 2. Code Implementation

- [x] 2.1 In `app/core/balancer/logic.py`:
  - Add `hard_owner_pool: bool = False` to `select_account`.
  - Update fallback condition to `allow_backoff_fallback and (len(in_error_backoff) > 1 or (in_error_backoff and hard_blocked_exists) or (in_error_backoff and hard_owner_pool))`.
- [x] 2.2 In `app/modules/proxy/_load_balancer/sticky_selection.py`:
  - Update `_select_with_stickiness` declaration and implementation to accept `hard_owner_pool: bool = False`.
  - Pass `hard_owner_pool=True` in `hard_sticky` selection branch.
  - Pass `hard_owner_pool=required_account_id is not None` in recursive call.
  - Pass `hard_owner_pool=hard_owner_pool` in no-sticky branch.
  - In `finish_selection`, pass `hard_owner_pool` to `_choose_from`, `pool_best`, and retention calls with `allow_backoff_fallback=hard_owner_pool`.
  - In `_select_account_preferring_budget_safe`, accept `hard_owner_pool` and pass to all `select_account` calls.
- [x] 2.3 In `app/modules/proxy/_load_balancer/unbound_selection.py`:
  - In `_select_from`, pass `hard_owner_pool=required_account_id is not None`.
- [x] 2.4 In `app/modules/proxy/load_balancer.py`:
  - Forward `hard_owner_pool` in `_select_with_stickiness`.

## 3. Verification & Testing

- [x] 3.1 In `tests/unit/test_load_balancer.py`:
  - Add `test_hard_owner_pool_admits_sole_backed_off_owner`.
  - Add `test_hard_owner_pool_still_fails_closed_on_persisted_unavailability`.
  - Add `test_hard_owner_pool_does_not_change_multi_account_selection`.
- [x] 3.2 In `tests/unit/test_load_balancer_contract.py`:
  - Add `test_required_continuity_owner_in_transient_backoff_is_still_admitted`.
  - Add `test_required_continuity_owner_paused_still_fails_closed`.
- [x] 3.3 In `tests/unit/test_select_with_stickiness.py`:
  - Add `test_hard_owner_pool_admits_backed_off_owner_through_stickiness`.
  - Add `test_hard_owner_pool_keeps_healthy_sibling_preference`.
  - Add `test_hard_owner_pool_retains_backed_off_pinned_owner`.
  - Add `test_hard_owner_pool_does_not_retain_a_persistently_blocked_owner`.
- [x] 3.4 Run unit tests and verify all pass.
