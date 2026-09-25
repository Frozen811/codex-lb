# Tasks: relogin-lifecycle-fuzz-pace-routing-health-tier

- [x] Implement Task 151: Decoupled automated re-login lifecycle and audit notifications (Issue #1959) <!-- id: 0 -->
  - [x] Emit `AuditService.log_async("account_reauth_required", ...)` in `app/modules/accounts/auth_manager.py` when an account transitions to `REAUTH_REQUIRED` <!-- id: 1 -->
  - [x] Add unit tests in `tests/unit/test_account_reauth_lifecycle.py` <!-- id: 2 -->
- [x] Implement Task 152: Property-based fuzz testing for load balancer state machine and routing invariants (Issue #1595) <!-- id: 3 -->
  - [x] Create hypothesis fuzz testing suite in `tests/unit/test_balancer_fuzz.py` <!-- id: 4 -->
  - [x] Validate invariant enforcement under arbitrary input states <!-- id: 5 -->
- [x] Implement Task 153: Pace-aware routing to land usage smoothly on reset boundaries (Issue #956) <!-- id: 6 -->
  - [x] Add `calculate_pace_deviation` and pace-aware routing ranking in `app/core/balancer/logic.py` <!-- id: 7 -->
  - [x] Add unit tests in `tests/unit/test_pace_aware_routing.py` <!-- id: 8 -->
- [x] Implement Task 154: Eliminate health-tier overlap in budget-safe account selection (Issue #578) <!-- id: 9 -->
  - [x] Filter `preferred_states` within `best_health_states` in `app/modules/proxy/_load_balancer/sticky_selection.py` <!-- id: 10 -->
  - [x] Add unit tests in `tests/unit/test_budget_safe_health_tier.py` <!-- id: 11 -->
- [x] Verification and Quality Gates <!-- id: 12 -->
  - [x] Run pytest on new and affected test suites <!-- id: 13 -->
  - [x] Run ruff linter check <!-- id: 14 -->
  - [x] Run OpenSpec validation <!-- id: 15 -->
  - [x] Verify simplicity budget (settings_tiers: 97/97) <!-- id: 16 -->
