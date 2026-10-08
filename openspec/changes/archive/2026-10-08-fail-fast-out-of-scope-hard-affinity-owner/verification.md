# Verification: caller-scoped-out owner fails without futile recovery

Date: 2026-10-08, Europe/Kiev. Baseline: `cbb295a8bcdb4d8ebae9c275c0d5754cfbaa6477`, fork main, clean worktree. This documentation-only commit retained the previously tested application source, but [CI #84](https://github.com/Frozen811/codex-lb/actions/runs/37729346951) exposed a latent timing-dependent selection error.

## Cloud evidence and cause

CI #84 ended **32 successful /3 failed jobs**. The primary [integration-core-5](https://github.com/Frozen811/codex-lb/actions/runs/37729346951/job/113154876994) failure was `test_codex_goal_restart_cannot_retire_owner_outside_api_key_scope`: it expected `hard_affinity_saturated` but received `upstream_request_timeout`. The integration-core and CI Required aggregates failed. Other applicable jobs and separate workflows passed.

Selection repeatedly reported the hard owner unavailable for the full 75-second request budget. The existing no-recovery-wait proof recognized explicit exclude_account_ids but did not receive the caller's allowed account collection, so an owner permanently outside that request's API-key scope looked like a temporarily unhealthy owner. Which loop boundary sampled the expiring budget determined the final error code. Both paths were closed failures, but the wait was futile and the exact error unstable.

The same cloud log contained repeated `SimpleNamespace.model_copy` errors from dashboard overlay application in stale-operation cleanup. The sticky-test helper provided an incomplete fake where the production Settings model is required. The unmodified API control passed locally only after **76.11 seconds**, confirming the undesired polling behavior rather than disproving the cloud failure.

## Red/green evidence and repair

A selector scope control failed before the edit because the out-of-pool owner had `hard_affinity_owner_excluded=False`; its in-scope rate-limited counterpart passed and remains the parity guard. A real API callback separately failed on that missing proof before any recovery wait, avoiding an expensive timing-dependent reproduction.

The existing caller account_ids constraint is carried into StickySelectionRequest as an optional frozen set. The existing boolean exclusion proof becomes true for a resolved hard owner either explicitly excluded or outside that supplied allowed set. An omitted set remains unrestricted; health and missing database rows are not inferred to be a policy exclusion. Public error envelopes and owner identity privacy remain unchanged.

The fixture now copies complete Settings while retaining its existing explicit budgets, including a matching 75-second stream budget. The repaired real route passed in **1.67 seconds**, selected the rejection exactly once, never dispatched upstream, and left the sticky owner/abandonment marker unchanged. Genuine in-scope owner recovery and soft/account-cap cases retain their old behavior.

## Focused validation

| Scope | Result |
|---|---|
| `uv run pytest -q tests/unit/test_load_balancer.py tests/unit/test_load_balancer_concurrency.py tests/unit/test_load_balancer_contract.py tests/unit/test_load_balancer_virtual_clock.py --tb=short --show-capture=no` | 497 PASS |
| `uv run pytest -q tests/integration/test_proxy_sticky_sessions.py --tb=short --show-capture=no` | 43 PASS |
| Whole-repo Ruff check /format, scoped ty on five edited Python files | PASS |
| Proxy architecture, cancellation safety, timing seams | PASS; balancer 3021-line ceiling retained |
| Strict OpenSpec 1.11.0 change/main validation | PASS, 68/68 capabilities |
| Simplicity budgets, delta/main comparison, and whitespace | PASS |

The two suites are disjoint: **540 passing cases**, no skips/xfails. Smaller controls overlap and are not added. Existing Starlette/AnyIO deprecation warnings remain. The line ceiling was preserved by condensing the existing metadata comment, not by increasing a ratchet.

## Completeness and publication boundary

One account-routing requirement and two scenarios are synchronized with main specs/context. The fixed selector proof is bound by out-of-scope/in-scope controls and the real API error/no-dispatch/no-mutation path. During the repair all 338 source rows and their qualified closure counts remained unchanged; no sixth task was selected. The preceding successful CI #83 and failed #84 remain exact-head history. The published repair SHA `5fd5b8141a13bde635ba0b38b283c6c81009a4ee` passed [CI #85](https://github.com/Frozen811/codex-lb/actions/runs/37774897114), attempt1: **35/35 jobs**, including the formerly failing integration-core-5 scope case and `CI Required`; separate Windows/release guards/simplicity bring the result to **39/39 applicable jobs**. [Publication evidence](publication.md) records the workflow URLs and exact source/ref identity.
