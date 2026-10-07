# Publication follow-up — 2026-10-07

The initial `76895643b0e6c811f46ac778a2138cba95e56dcf` was a local main commit; it had not been pushed. After the user's follow-up pointing to GitHub main, publication is authorized to `Frozen811/codex-lb:main`.

Fetched main: `2483ea459e24b4ff7e5e681326e944a96f47a18c`. The new parent already fixes monthly classification and unknown Team credits and closes UP-ISSUE-1918/1367 and UP-PR-2468 in registry section 59. Its source, tests, archive, evidence and all 337 queue rows outside UP-ISSUE-2554 are preserved. The initial local report becomes section 60. The new publication adds UP-ISSUE-2554 closure and F-082 closure without counting the other three source records twice. Queue: 338 records, 96 local closures, 7 partial, 235 НЕ ПРОВЕРЕНО.

## Rebase resolution

- Rebuild the registry from fetched main, retain its three overlapping closure/evidence rows, update only UP-ISSUE-2554 and F-082, and append section 60.
- Keep exactly one Edu parameter decorator in the quota regression (both commits independently added it).
- Preserve the new Team monthly route/recovery and API regressions plus the local lease/depth/Edu API regressions.
- Retain the corrected unknown Team monthly credits; no invented capacity is restored.

## Fresh verification before push

`uv run --no-sync pytest -q tests/unit/test_openai_requests.py tests/unit/test_request_policy.py tests/unit/test_passthrough_request_fields.py tests/unit/test_lease_pressure_contracts.py tests/unit/test_routing_tunables.py tests/unit/test_usage.py tests/unit/test_account_mappers.py tests/unit/test_quota_planner.py tests/unit/test_responses_requests.py tests/unit/test_chat_request_mapping.py tests/integration/test_passthrough_request_validation.py tests/integration/test_load_balancer_integration.py tests/integration/test_quota_planner_api.py --tb=short` — **669 passed**, 64.26s.

`uv run --no-sync pytest -q tests/integration/test_accounts_api_extended.py -k 'monthly or edu' --tb=short` — **44 passed /32 deselected**, 35.61s.

Distinct Python total: **713 passed**, no selected-case failures/skips/xfails. Existing Starlette/AnyIO deprecation remains. The 673-count initial report is historical and is not added to this total.

`make lint` — PASS (proxy architecture, cancellation, timing, settings98/98, migration single-head, full Ruff and format1481). Scoped `ty check` on the three changed app modules, simplicity budgets, `git diff --check`, strict OpenSpec **68/68** — PASS.

Frontend, from `frontend/`: `node node_modules/vitest/vitest.mjs run src/features/dashboard/components/account-card.test.tsx src/features/dashboard/components/account-list.test.tsx` — **29 passed**, 6.87s, after rebase. Tested file hashes after rebase live in publication-files.json; the original verified-files.json describes the earlier local tree and remains historical.

## Remote verification

The publication command is a normal, non-forced `git push origin main`. After it succeeds, compare local `git rev-parse main` with `git ls-remote origin refs/heads/main`. The fixing SHA is the commit that introduces this file; `git log --diff-filter=A -1 --format=%H -- openspec/changes/archive/2026-10-07-verify-five-depth-and-quota-contracts/publication.md` resolves it without self-referential metadata. Cloud CI/release/deployment are separate scopes and are not inferred from push.
