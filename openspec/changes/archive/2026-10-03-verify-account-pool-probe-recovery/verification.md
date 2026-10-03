# Verification: account pool, Force Probe, and weekly reserve recovery

Date: 2026-10-03. Checkout: `C:\codex-lb`. Base HEAD: `f52adb72`.
Exactly three registry entries: UP-PR-2523, UP-PR-2524, UP-PR-2527. All results refer to the local working tree; earlier unrelated changes were preserved.

## Result

| Dimension | Evidence |
| --- | --- |
| Completeness | 9/9 tasks; exactly three registry rows updated |
| Correctness | Both delta requirements and all nine scenarios covered by tests; existing probe/routing contracts verified |
| Coherence | Shared credential predicate, existing Resume callback/API, one metrics query; no new settings, schema, dependencies, or navigation |

No actionable findings remain in the implemented local scope. The primary agent reviewed the final source and contract independently of the original source author; no delegated reviewer was used.

## UP-PR-2523: metric availability (F-055)

Nine real database/ASGI exposition cases reproduced `accounts_available = 1` when routing excluded the account. Each of the three established access-rejection reasons was combined with future, unknown, or unreadable expiry. The projection omitted the stored reason when calling the existing shared predicate.

The fix passes the reason from the already-loaded snapshot. All nine cases now produce availability zero while retaining the `reauth_required` inventory count. Repair to a refresh-only warning and usable credentials makes the next quiet-pool scrape report one. Expiry, deletion, explicit status zeroes, overlapping refreshes, optional dependency, and multiprocess regressions pass. A database failure returns 503 and recovery loads a fresh committed status instead of the old snapshot.

The initial exporter tests were skipped because optional Prometheus was absent. `uv sync --frozen --extra metrics` installed locked `prometheus-client==0.26.0`; final exporter/multiprocess tests executed without skips. Dependency metadata and lockfile were unchanged.

## UP-PR-2524: Force Probe snapshot settlement

The existing ORM snapshot fix is confirmed through the real dashboard route and rollback/close repositories. Existing tests cover missing/partial rows, monthly applicability, zero-capacity legacy primary usage, newer health failures, lease-only changes, and rejected/network-failed probes.

Three added route cases verify weekly-primary usage at 87% (above the 85% short-window threshold, below the 90% long-window threshold), elapsed primary, and elapsed secondary rows. Accepted probes advance recovery to healthy, clear transient errors, avoid settlement errors, and preserve stored history. An initial 96% weekly test exceeded the actual long-window drain threshold; the harness was corrected to 87%, without changing product thresholds.

## UP-PR-2527: weekly recovery and manual Resume (F-056)

Fourteen real Responses cases cover both `/v1/responses` and `/backend-api/codex/responses`, committed weekly-primary rows, persisted block markers, replica runtime, and an existing sticky owner. Post-debounce fresh 87% weekly evidence recovers to active, clears expired quota holds, dispatches to the same account, and preserves storage/ownership. Missing, pre-block, same-second, exhausted, and within-debounce evidence cannot recover. An independent rate-limit retains its persisted deadline and local cooldown. Exhaustion preserves HTTP 429 `usage_limit_reached`. Stored weekly data never becomes a synthetic 5h row.

Dashboard Resume was absent for `quota_exceeded` although backend reactivation already supported it. Three frontend cases failed before the change. The existing predicate now admits that status, with callback-once and busy/read-only controls; reauthentication remains protected. A real API/CAS test verifies removal of persisted quota markers and preservation of the owner.

The Chromium regression renders the Accounts route with API fixtures, clicks Resume, observes exactly one POST to the existing reactivation route, and verifies active actions after refresh. [Before](screenshots/quota-resume-before.png) and [after](screenshots/quota-resume-after.png) screenshots were visually inspected. Browser fixtures do not establish deployed-backend correctness; backend tests use real database/API paths.

## Validation

The main run passed **716 Python tests** across: `test_weekly_reserve_recovery_contracts`, `test_accounts_api_probe`, `test_account_pool_metrics`, `test_metrics`, `test_account_metrics_multiprocess`, `test_account_metrics`, `test_load_balancer_concurrency`, `test_accounts_service_probe`, `test_load_balancer`, and `test_usage_updater`.

The subsequently added manual Resume case plus two existing reactivation API controls passed separately: **3 passed**, totaling **719 distinct Python tests**. After final refresh-recovery and assertion additions, all **69 tests** in the three integration files passed again; reruns are not added to the distinct count. Account-actions/mutation-hook frontend tests: **24 passed**. Chromium Resume smoke: **1 passed**. Total: **744 distinct cases**.

- Targeted Ruff check/format (four Python files), targeted `ty`, frontend TypeScript and ESLint: PASS.
- Proxy architecture, cancellation safety, timing seams, settings tiers, simplicity budgets, scoped diff check: PASS.
- Change strict validation and **68/68** main specs: PASS; both delta blocks match synchronized main requirements.
- Existing warnings: Starlette/AnyIO deprecation and an unawaited AsyncMock coroutine in the older metric shim unit fixture. No new failure or skip remains.

## Residuals

Real upstream accounts, original user incidents, deployed replicas, published packages/images/Pages, current-head cloud CI, CodeRabbit, and release gates remain unverified. Historical upstream merged/closed labels are not current GitHub merge assertions. No commit, push, PR, release, or deployment was performed.

## Source fingerprints

- app\modules\proxy\account_cache.py: `2b17ac6bc0eb7f0573ed375697443ab4e6b064112617fc3bbf176852e94a0027`
- frontend\src\features\accounts\components\account-actions.tsx: `d7f981a571e0b287c682c65cc337e311a380a7f44a2ee392793eca924526488f`
- tests\integration\test_weekly_reserve_recovery_contracts.py: `a5dc771203e19d1620034b522a7f6a38b4fb7ebc7104809f680efe137439ac7e`
- tests\integration\test_account_pool_metrics.py: `6aa2fe39e334146e5f1a7a24c1f84a373b3a15cc5336c7af4449b5a046ec007c`
- tests\integration\test_accounts_api_probe.py: `ce537ec4c608b3e5b6e252814e625846deba7d5fd72e500167e166eb682cf8db`
- frontend\src\features\accounts\components\account-actions.test.tsx: `bc256ae235f9c55140171bf46fd96b526b56168b19b09daf4b2789c8ca692b91`
- frontend\browser-smoke\dashboard.spec.ts: `74b939dc20119b917b198f018371b3f20c9f70e1572f16fbb5400900915ece0a`
