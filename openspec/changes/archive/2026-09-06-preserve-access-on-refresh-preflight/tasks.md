# Tasks

- [x] Catch credential failures in `AuthManager.ensure_fresh` preflight refresh.
- [x] Verify database access token expiration and adopt unexpired state without raising `RefreshError`.
- [x] Create comprehensive integration tests in `tests/integration/test_auth_preflight.py`.
- [x] Add end-to-end regression test in `tests/integration/test_proxy_responses.py`.
- [x] Sync delta spec to `openspec/specs/usage-refresh-policy/spec.md`.
