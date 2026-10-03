# Verification: repair-auth-log-audit-contracts

Date: 2026-10-03. Base HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`.
Evidence applies to the current uncommitted working tree. Existing batches were preserved.
Exactly three registry items: UP-ISSUE-2028, UP-PR-2487, UP-PR-2490.

## Completeness

All three selected scopes have product-path evidence. Only logging required a production repair. TOTP normalization and refresh diagnostics were already implemented and have been independently verified with broader regression coverage.

## UP-ISSUE-2028 / F-051

The initial new suite, before the runtime edit, returned **56 failed / 32 passed**. Failing examples include quoted/repeated commas, malformed auth parameters, unquoted JSON-style keys, placeholder tails, a parameter named `status`, and ampersand-separated credential tails. All values are inert sentinels.

The runtime now replaces an explicit authorization field before generic token substitutions. Complete quoted values retain delimiters; other values mask the current line remainder. This deliberately drops same-line diagnostic-looking text after an unquoted field. Structured extras and following lines retain context. The old credential-boundary grammar was removed from this field pass; standalone Basic/Bearer behavior remains covered by the existing suite.

`tests/unit/test_auth_log_audit_contracts.py`: **94 passed**. It covers five output surfaces (error fields, text/JSON message and exception rendering), LF/CRLF/CR boundaries and idempotency, actual text/JSON log-file writes, quoted field context and unterminated values. Three existing expectations were updated to the explicit new separator policy; all existing structured logging tests pass.

## UP-PR-2487

Real application HTTP routes test five digit classes through TOTP setup confirmation and subsequent verification. Invalid values return HTTP400 `invalid_totp_code` and retain enrollment, replay step and session cookie. A valid formatted ASCII code subsequently succeeds and advances the replay counter. Existing time-window and replay tests also pass. No production TOTP edit was needed.

## UP-PR-2490

A real local aiohttp OAuth server receives the refresh form payload. The real account manager, owned per-task database session and AccountsRepository serve overlapping private and ordinary callers in both arrival orders. Ten combinations cover HTTP401 revoked/invalidated, HTTP400 expired, HTTP503 hostile provider code/message and HTTP429 without a provider code.

Each combination makes one provider call and emits one account-correlatable warning. Its account reference matches the documented SHA-256 prefix, safe codes and classification flags are retained, an unknown code becomes `other`, and account identity/email/tokens/provider body/log-injection sentinels do not appear in call-phase logs. Permanent failures persist REAUTH_REQUIRED; transient failures retain ACTIVE; credential ciphertexts remain unchanged. The test preserves existing error classification (including non-permanent `refresh_token_revoked`), rather than broadening this diagnostic task into a routing-policy change.

Existing auth-manager tests separately cover transport flags, local route/admission failures, no provider call and claim-timeout release. No production refresh edit was needed. The test uses a distinct deterministic account identity per case because the production singleflight error cache intentionally outlives a test database reset; its initial cache collision was a fixture issue, not a product defect.

## Final checks

- `uv run pytest tests/integration/test_refresh_failure_diagnostics_wire.py tests/integration/test_dashboard_totp_auth.py tests/unit/test_auth_log_audit_contracts.py tests/unit/test_structured_logging.py tests/unit/test_totp.py tests/unit/test_auth_manager.py -q --tb=short`: **279 passed**, one existing Starlette/AnyIO deprecation warning. Intermediate runs are not summed.
- `uv run --frozen --extra metrics pytest tests/integration/test_metrics_server_logging.py -q --tb=short`: **1 passed** independently. Optional metrics dependency installed from the frozen lock; no lockfile change.
- Scoped Ruff check/format and targeted ty check: **PASS**.
- Proxy architecture, cancellation safety, proxy timing seams, settings-tier and simplicity-budget checks: **PASS**, limits unchanged.
- Strict OpenSpec change validation: **PASS**. Strict main-spec validation: **68 passed / 0 failed**.
- Focused diff whitespace validation: **PASS**.

## Correctness and coherence review

| Delta scenario | Evidence |
|---|---|
| Authorization does not swallow the next traceback line | Existing structured logging tests and new CR/LF cases |
| Unterminated JSON secret | Existing structured logging tests |
| Bearer glued colon tail | Existing structured logging tests |
| Authorization same-line truncation | Existing structured logging tests with explicit-field policy |
| Line endings and idempotency | New parameterized tests, including repeated redaction |
| Quoted comma and malformed auth parameters | Original upstream probes plus status/ampersand cases through five surfaces and log files |
| Complete quoted fields preserve context | Exact-output JSON/repr/bytes tests |
| Placeholder tails are not trusted | Sentinel cases through all output surfaces |
| Following diagnostic lines survive | LF, CRLF and CR tests |

Current source and scenarios were reviewed again without a separate reviewer agent. No missing requirement implementation or critical issue remains. Main spec/context and the troubleshooting guide reflect the new operator contract. Admin-auth and account-routing requirements remain unchanged and verified.

Codebase-memory returned the old redactor source even after a fast reindex. Final implementation/impact review therefore used current filesystem source and runtime tests; graph snippets were not treated as proof of the final implementation.

## Limits

Native Windows focused tests and local synthetic OAuth traffic are verified. The uvloop-only logging-handler suite is unavailable on this Windows environment and is not claimed as passed. Public packages/images, cloud CI, deployed replicas and real OpenAI credentials/traffic remain outside this batch. No commit, push, release or deployment occurred.
