# Verification — five registry records

Date: 2026-10-07, Europe/Kiev. Base: `126c0323` (full SHA in source-snapshot.json); initially clean `work`, then a local `main` created at the same head at the user's explicit request. No remote publication or CI run is claimed.

## Records and evidence

| Record | Verified behavior | Evidence |
|---|---|---|
| F-082 | The historical 12-case accepted-boundary selection now passes on the locked environment (Pydantic 2.13.5 / pydantic-core 2.46.5). An extra JSON field at depth 300 still failed serialization; the new guard closes that bypass. Depth 200 remains accepted without copying/coercing the source object, depths 201/300 are field-local validation errors, nested controls name their full field path. | test_passthrough_request_fields.py, test_passthrough_request_validation.py; all five native/compat/chat/compact HTTP routes return 400 for deep extensions; golden forwarded bytes and OpenAPI generation pass. |
| UP-ISSUE-2554 | Existing plan-independent lease units, sub-exhaustion pressure ceiling and persisted-usage fallback are independently verified. Two real SQLite accounts (95%/38%) each hold a 10,240-token stream lease; the lighter account wins with weights 0, 1 and 10,000, on Plus and Pro. Leases are released and counters return to zero. | test_lease_pressure_contracts.py, test_routing_tunables.py, test_relative_availability_keeps_usage_order_with_two_open_leases. Deterministic top-K=1 isolates ranking; existing selection tests cover seeded/fallback behavior. |
| UP-ISSUE-1918 | Explicit exhausted Edu weekly quota survives an elapsed older reset and missing deadline/block-marker combinations; a later available sample permits recovery. Accounts API reports quota_exceeded, zero weekly remaining, 10080-minute window and a reset. | Extended real-SQLite load-balancer regression (Plus/Edu) and test_edu_exhaustion_keeps_weekly_hold_and_quota_projection; ordinary quota/advisory policies remain in force. |
| UP-ISSUE-1367 | Existing Team monthly mapping retains 43200-minute monthly quota, hides stale 5h/weekly values, and renders Monthly in card/list. | 6 monthly-only Accounts API cases (Free/Team × absent/primary/secondary older window), account mappers and 29 existing card/list frontend tests. No dashboard rendering code was changed. |
| UP-PR-2468 | Existing invalid-timezone rejection is atomic, including parent-relative keys and embedded NUL; valid names trim, omitted/null/blank updates retain the stored value, malformed legacy keys remain stored while forecast/routing use UTC. | Full quota planner unit/API selections; expanded test_quota_planner_rejects_invalid_timezone_without_saving. |

The four upstream queue records had НЕ ПРОВЕРЕНО status in this fork registry, independently of upstream open/closed state. Fresh upstream metadata/bodies are preserved in upstream-snapshot.json; original registry lines in source-snapshot.json. Already present quota/timezone implementations were verified, not reimplemented.

## Red-before and final commands

Before app edits:
- `uv run --frozen pytest -q tests/unit/test_passthrough_request_fields.py -k nesting_at_the_limit --tb=short` — **12 passed / 73 deselected** (historical F-082 no longer reproduces on this checkout).
- A standalone valid native request with a 300-level extra JSON object raised `ValueError: Circular reference detected (depth exceeded)` in serialization.
- `uv run --no-sync pytest -q tests/unit/test_passthrough_request_fields.py -k extension --tb=short` — **10 failed / 5 passed** before the new guard (201/300-depth fields were accepted).

Final disjoint scopes, **673 Python passed**:
1. `uv run --no-sync pytest -q tests/unit/test_openai_requests.py tests/unit/test_request_policy.py tests/unit/test_passthrough_request_fields.py tests/unit/test_lease_pressure_contracts.py tests/unit/test_routing_tunables.py tests/unit/test_usage.py tests/unit/test_account_mappers.py tests/unit/test_quota_planner.py --tb=short` — **489 passed**, 8.03s.
2. `uv run --no-sync pytest -q tests/unit/test_responses_requests.py tests/unit/test_chat_request_mapping.py tests/integration/test_passthrough_request_validation.py tests/integration/test_load_balancer_integration.py tests/integration/test_quota_planner_api.py --tb=short` — **177 passed**, 45.10s.
3. `uv run --no-sync pytest -q tests/integration/test_accounts_api_extended.py -k 'monthly_only_quota or edu_exhaustion' --tb=short` — **7 passed / 38 deselected**, 4.19s.

The final no-copy assertion was strengthened after scope 1; its focused extension selection was rerun: **18 passed / 85 deselected**, 0.15s (overlaps scope 1). Earlier 134/173 intermediate runs overlap final scopes and are not added to totals. No failures/skips/xfails in the selected final Python cases. Existing Starlette/AnyIO deprecation warning is retained.

Frontend: from `frontend/`, `node node_modules/vitest/vitest.mjs run src/features/dashboard/components/account-card.test.tsx src/features/dashboard/components/account-list.test.tsx` — **29 passed**, 5.31s. Existing Vite plugin recommendation is retained.

Static/contract checks:
- `uv run --no-sync ruff check .` — PASS.
- `uv run --no-sync ruff format --check .` — PASS, 1480 files.
- `uv run --no-sync ty check app/core/openai/requests.py app/core/openai/chat_requests.py app/core/openai/v1_requests.py` — PASS.
- `make architecture-check` — proxy architecture, cancellation, timing, settings 98/98 and single-head migration topology PASS.
- `python .github/scripts/check_simplicity_budgets.py` — PASS, all budgets unchanged.
- `npx --yes @fission-ai/openspec@1.11.0 validate verify-five-depth-and-quota-contracts --strict` — PASS before archive; verified archive syncs the two modified requirements.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs` — 68/68 PASS, also rerun strictly after archive. The archived delta was additionally copied to a disposable standalone OpenSpec root and passed strict validation there; archived names are not active change IDs in the CLI.
- `git diff --check` — PASS.

## Limits and commit identity

Local Python/API/SQLite and component tests are evidence for this scope only. Full repository suites, provider traffic, browser screenshots, PostgreSQL/MySQL/distributed runtime, cloud CI, releases and deployment were not run. Earlier external/partial findings, including CI-04/F-045, are unchanged. Exactly four upstream queue rows plus F-082 are closed locally; remaining 334 queue rows retain their original bytes/status. Queue becomes **338 records: 94 local closures, 7 partial, 237 НЕ ПРОВЕРЕНО**.

The fixing SHA is the commit that introduces this archive and registry section 60; obtain it with `git log -1 --format=%H -- openspec/changes/archive/2026-10-07-verify-five-depth-and-quota-contracts/verification.md`. Verification files precede the user-requested local main commit; no new remote CI evidence is inferred from that commit.

## Publication update

The local-only result above is historical. This package was subsequently rebased onto published main `2483ea45`, preserving its monthly fixes and overlapping closures. [Publication evidence](publication.md) records fresh 713-test verification, the registry numbering/count correction and the remote verification procedure.
