# Five account placement contracts - local verification, 2026-10-13

Initial HEAD: `cfc939cc69e6534996365a348b74eaf414283f34`, branch `main`, clean working tree. Exactly five initially `НЕ ПРОВЕРЕНО` source rows are owned by this batch. No commit, push, PR, merge, release or deployment was performed.

| Registry row | Result and product evidence |
|---|---|
| UP-ISSUE-1576 | Fixed ORM access after repository teardown, omitted transport routing headers, strict-route/required-owner conflicts, and missing unavailable-target error naming. New tests exercise real HTTP Responses/compact/bridge, four aliases including trailing slash, both native WS routes and warm native/bridge owner refusal. Header overrides select B instead of registered A; API-key scope remains binding and no reservation remains reserved after refusal. |
| UP-ISSUE-1307 | Fixed retained bridge TTL independently of sticky-row expiration. Explicit child idle metadata caps hard and soft affinity, preserves shorter 60/120-second policy and ordinary parent behavior. New public-route tests cover creation, reuse, idle pruning, socket close and zero residual account pressure. |
| UP-PR-2448 | Fixed fresh-child diversification being suppressed by the bridge's `follow_up` stage hint. Fresh account-neutral lineage plus no child mapping/required owner permits the advisory alternate attempt; unavailable siblings fall back within the same deadline, established children retain their mapping. Real Codex HTTP routes and slash alias exercise all three cases; helper suite and native routing regressions cover ownership exclusions. Generic `/v1/responses` keeps its deliberately non-Codex affinity mode. |
| UP-ISSUE-2327 | Existing pinned-probe recovery independently verified. New real account API/SQLite tests preserve the requested model and account, clear available quota holds, retain failed/exhausted holds and preserve a concurrent operator pause. Existing probe/usage suites cover usage-fetch failure and advisory settlement; production code for this row required no additional change. |
| UP-PR-2117 | Existing revoked-token/permanent-refresh retirement independently verified at Responses and refresh/compact transport paths. Regression selection covers revoked event failover, hard owner refusal, repeated exclusion, guarded operator repair, lease release before failover and settlement ordering. Production code for this row required no additional change. |

## Reproductions and corrected behavior

- New public routing test initially raised `DetachedInstanceError` when `resolve_model_account_override` accessed an expired Account after repository teardown. Identity extraction now stays inside the session.
- With that lifetime defect corrected, header override tests still dispatched `placement-a` instead of the requested `placement-b`; transport callers now pass the routing headers.
- Child route test observed a retained TTL of `3600.0` despite a configured child TTL of `120`. It now observes `120` and proves idle cleanup.
- Fresh Codex child lineage was eligible, but bridge selection uses `follow_up`; the old first-turn-only guard skipped placement preference. The stage gate now admits this soft header classification while lineage proof and established mappings continue to govern eligibility.
- Intermediate fixture errors (positional connector arguments, loopback bootstrap, response ID field, mocked settings cache and real API-key enablement) were corrected in the new harness. They are not counted as product defects or final passes.

## Final focused test evidence

**377 distinct PASS, 0 skips, 0 xfails.** These four final selections have disjoint test files:

1. `uv run pytest -q tests/unit/test_model_account_routing.py tests/unit/test_affinity_subagent_ttl.py tests/unit/test_subagent_account_preference.py tests/unit/test_accounts_service_probe.py tests/unit/test_usage_updater.py --tb=short --maxfail=2`: **208 passed**.
2. `uv run pytest -q tests/integration/test_account_placement_contracts.py --tb=short`: **58 passed**. This includes 12 route/header cases, 4 unavailable targets, 4 warm bridge owner conflicts, 8 child creation/cleanup cases, 4 native cases, 4 child reuse cases, 12 key-scope cases, 6 Codex child placement cases and 4 probe boundaries.
3. `uv run pytest -q tests/integration/test_accounts_api_probe.py tests/integration/test_proxy_transient_retry.py tests/integration/test_proxy_responses.py tests/integration/test_token_refresh_claims.py tests/integration/test_proxy_websocket_responses.py tests/unit/test_proxy_utils.py -k 'probe or revoked or permanent_refresh or auth_recovery or auth_invalidation' --tb=short --maxfail=3`: **102 passed**, 1990 deselected.
4. `uv run pytest -q tests/integration/test_http_responses_bridge.py tests/integration/test_cache_locality_fix.py -k 'idle or ttl' --tb=short --maxfail=2`: **9 passed**, 235 deselected.

Each run reports the existing Starlette `anyio.abc.BlockingPortal` deprecation. Test teardown can log the existing clean-SQLite-shutdown lifetime-lock warning for its disposable test database; no application or production database was used.

## Static, specification and scope verification

- Ruff check and format check passed on all 12 changed Python paths. Scoped ty passed on all 10 changed application paths.
- Proxy architecture, cancellation safety, timing seams and settings tiers passed without changing guard limits. Migration topology: 275 revisions, single existing `20261010_000000_add_source_catalog_discovery` head; no revision added or edited. Static migration duration guard passed; no runtime migration-duration measurement is claimed.
- Simplicity budgets passed: README 218/225 lines, headings 10/10, env example 54/60, core navigation 5/5, extra tracked root files 0/0.
- Strict delta validation passed. Three added requirements / 11 scenarios were synced to account-routing and sticky-session-operations; strict canonical validation passed **68/68**. Stable context explains examples, decisions, ownership constraints and failure modes. Existing spec/context byte prefixes are preserved in `prefixes.json`.
- All eight tasks completed; verified change archived. Exactly five registry rows updated and reread; **333/333** other source rows remain byte-for-byte unchanged, with hashes in `closure.json`. Queue: 338 records, 198 local closures, 2 not applicable, 8 partial, 130 unverified.
- Full application diff and new regression suite reviewed; final whitespace check passed. Initial tree was clean; no unrelated modifications were included.

## Practical limits

This is local Windows/Python/real disposable SQLite evidence with fake upstream inference responses and HTTP probe status. Probe recovery retains the existing successful-HTTP-status plus fresh-available-usage contract; actual provider SSE terminal completion and matching historical provider bucket are not attested by these tests. Real Desktop/provider traffic, PostgreSQL/MySQL execution, distributed races, hosted current-head CI, public artifacts and production remain separate. Previous partials, F-045 and CI-04 are unchanged. No release authority or external upstream PR status is inferred from these results.
