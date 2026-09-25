## 1. Specification

- [x] 1.1 Specify routes and operations for `alpha/history/v2` and `alpha/notes/v2`.
- [x] 1.2 Specify affinity rules including child-thread and subagent lineage.

## 2. Implementation

- [x] 2.1 Update `_sticky_key_for_codex_control_request` in `app/modules/proxy/affinity.py` for thread affinity and subagent parent linkage.
- [x] 2.2 Register `alpha/history/v2/{operation}` and `alpha/notes/v2/{operation}` route handlers in `app/modules/proxy/api.py`.
- [x] 2.3 Update `_FAIL_CLOSED_HTTP_ROUTES` in `tests/integration/test_daybreak_capability_routes.py`.

## 3. Verification

- [x] 3.1 Unit and integration regression coverage for all 10 operations, trailing slashes, thread identity, and unavailable owner handling.
- [x] 3.2 Verify test inventory and proxy architecture checks pass.
