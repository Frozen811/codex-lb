# Verification: five dashboard inventory contracts

Date: 2026-10-05, Europe/Kiev. Base HEAD: `f987d08e69978ee6452c4e5997b11e80a81ba5f2`.
This batch processes exactly five previously unverified registry records. Its result is local implementation and verification; upstream PRs remain separate objects.

## Source provenance

Fresh authenticated GitHub REST reads confirmed all five PRs OPEN and not merged. The public PR pages were also read. Patches were adapted to current source; author test claims were not accepted as local evidence.

| Record | Source head | Local result |
|---|---|---|
| [UP-PR-2565](https://github.com/Soju06/codex-lb/pull/2565) | `b2fe90c502c0032c7857dbd64ec9664506a3e342` | Complete loaded account inventory distributions with accessible legends and empty/error states |
| [UP-PR-2566](https://github.com/Soju06/codex-lb/pull/2566) | `0a16dedcf3d2f56476f32e5c16ad0f4bfbd5e188` | Optional persisted compact key list, sorting, pagination, details, permissions and consistent unused evidence |
| [UP-PR-2576](https://github.com/Soju06/codex-lb/pull/2576) | `b0d4575fbd505155236167322121adec0498d86c` | Six supported image adapters in typed dashboard catalog and key allowlists; Automations filter |
| [UP-PR-2577](https://github.com/Soju06/codex-lb/pull/2577) | `acd558b0e715ab34b6ad7e9f108bc2904f359a20` | Accessible 72-hour credit-expiry marker with current-time resubscription and timer teardown |
| [UP-PR-2578](https://github.com/Soju06/codex-lb/pull/2578) | `7383db7014b3187483e792480b6ffa3e24b11c2c` | Eight status/quota sort choices, unknown-last semantics, deterministic ties and selection preservation |

## Reproduction and independent adaptations

- Before production edits, the ten-file frontend selection produced **31 failed /60 passed** in 57.46s. Six actual `/api/models` and key-allowlist cases produced **6 failed** in 5.52s.
- Additional tests against the initially adapted upstream behavior produced **4 failed /15 passed**: positive token, cached-token or cost evidence was classified as unused, and a hidden expiry clock was stale when enabled again. The shared usage predicate now recognizes those recorded usage fields. A list-local external clock subscription refreshes on visibility changes without an impure render-time clock read, and owns one cleaned-up minute timer.
- Current support includes `gpt-image-2.5-flare` and `gpt-image-2.5-sunburst` in addition to the upstream proposal's four image identifiers. All six are covered by actual dashboard responses and image validation.
- Three old normative blocks were reconciled: native catalog equality now distinguishes dashboard adapters/sources, and historical reset-sort wording recognizes the current Most reset credits default. Existing scenarios and unrelated requirements remain intact.

## Completeness, correctness and coherence

| Contract | Implementation | Verification |
|---|---|---|
| Full inventory distributions | Shared DonutChart distribution mode, AccountDistributionCharts, AccountsPage | Donut/page tests; all statuses, blank/unknown plans, refreshed counts, empty/error reads, filters; Accounts flow and rendered desktop/mobile plots |
| Compact key inventory | APIs page, list, reusable quota rows and shared usage predicate | All five sort columns, both directions, unknown-last values, 26-key pagination, combined filters, persisted/blocked storage, read-only detail actions, positive token/cost cases |
| Image picker | Shared supported identifiers, typed dashboard schemas/route, frontend metadata, Automations filter | Bootstrap/refreshed/empty registries, public/hidden collisions, sources, exact-once identifiers, create/edit persistence, actual permission refusal and positive read, public catalogs unchanged |
| Expiry warning | Credit badge and visibility-aware list clock | Exact 72h and now boundaries, invalid/missing/elapsed time, zero count, both visibility settings, data refresh, no-refetch transition, hide/re-enable and unmount cleanup |
| Account sorting | Existing deterministic sorting and selector | Both directions for each quota/status mode, zero/missing/non-finite values, all statuses, stable ties/input preservation, filters and browser selection preservation |

Eight normative requirements and 21 scenarios are synchronized exactly with the two main capabilities. Stable context was promoted to their context.md files; rendered documentation links its owning specs. No configuration, dependencies, database migrations, core navigation items, README sections or changelog edits were added.

Graph navigation established the existing symbols and direct dependencies. Literal graph-backed searches did not return expected route strings; current source and runtime tests were used for those edges and new symbols. No independent agent was spawned. Review consisted of direct source/patch inspection, fresh negative cases and product-path tests.

## Passing local checks

| Check | Result |
|---|---|
| Final frontend selection below | **142 passed**, 14 files, 58.49s; no failures or skips |
| `test_v1_models.py` + `test_images_schemas.py` | **218 passed**, 101.37s; no skips |
| Actual missing/positive dashboard-read checks | **2 passed**, 1.57s |
| Live application dashboard session dependency matrix | **1 passed**, 0.69s |
| Final Playwright desktop/mobile captures | **2 passed**, 9.0s; sort selection preserved, image picker present, overflow checks pass |
| Full frontend ESLint; TypeScript build; production Vite build | PASS |
| Scoped Ruff, format and app typing | PASS; five Python files formatted; ty passed for the three changed app modules |
| Proxy architecture, cancellation safety, proxy timing seams | PASS |
| Settings tiers | PASS, 98/98 |
| Simplicity budgets | PASS; README 218/225 lines, 10/10 headings; env 54/60; nav 5/5; root 0/0 |
| Strict change and main OpenSpec | PASS; main **68/68** |
| Git whitespace | PASS |

Separate five-module edge selection: **45 passed /19.36s**. Earlier 98-case pass and the 139-pass diagnostic run overlap with final coverage and are not added to its count. The diagnostic run's three failures were invalid test-factory inputs: the schema rejected non-finite values before sorting; direct in-memory test values corrected that fixture. Initial screenshot attempts used an overbroad Vite proxy route and stale locators; corrected navigation and reduced-motion rendering produced the final passing captures with visible pie sectors. Wrong local checker filenames were corrected before reporting PASS.

Backend tests emit the existing Starlette/AnyIO portal deprecation; frontend emits the existing jsdom scrollTo and Vite plugin notices. These are environment notices, not skipped tests or whole-repository certification.

## Reproduction commands

From `frontend/`:

```powershell
node node_modules/vitest/vitest.mjs run src/components/donut-chart.test.tsx src/features/accounts/components/accounts-page.test.tsx src/features/accounts/components/account-list-expiry.test.tsx src/features/accounts/components/account-list-sorting.test.tsx src/features/accounts/components/account-list.test.tsx src/features/accounts/components/account-list-item.test.tsx src/features/accounts/sorting.test.ts src/features/apis/components/api-list.test.tsx src/features/apis/components/apis-page.test.tsx src/features/api-keys/components/api-keys-overview.test.tsx src/features/api-keys/usage.test.ts src/__integration__/api-keys-flow.test.tsx src/__integration__/automations-flow.test.tsx src/__integration__/accounts-flow.test.tsx
node node_modules/eslint/bin/eslint.js .
node node_modules/@typescript/native/bin/tsc -b
node node_modules/vite/bin/vite.js build
$env:INVENTORY_STAGE='after'
$env:INVENTORY_EVIDENCE_DIR=(Resolve-Path ../openspec/changes/archive/2026-10-05-repair-five-dashboard-inventory-contracts/evidence).Path
node node_modules/@playwright/test/cli.js test --config browser-smoke/inventory-contracts.config.ts
```

From the repository root:

```powershell
uv run pytest tests/integration/test_v1_models.py tests/unit/test_images_schemas.py -q
uv run pytest tests/integration/test_dashboard_permission_gates.py -k 'image_picker_catalog or account_window_projections' -q
uv run pytest tests/integration/test_dashboard_route_permission_matrix.py -k every_dashboard_route_validates_the_session -q
uv run ruff check app/core/openai/images.py app/modules/dashboard/api.py app/modules/dashboard/schemas.py tests/integration/test_v1_models.py tests/integration/test_dashboard_permission_gates.py
uv run ruff format --check app/core/openai/images.py app/modules/dashboard/api.py app/modules/dashboard/schemas.py tests/integration/test_v1_models.py tests/integration/test_dashboard_permission_gates.py
uv run ty check app/core/openai/images.py app/modules/dashboard/api.py app/modules/dashboard/schemas.py
uv run python scripts/check_proxy_architecture.py
uv run python scripts/check_cancellation_safety.py
uv run python scripts/check_proxy_timing_seams.py
uv run python scripts/check_settings_tiers.py
uv run python .github/scripts/check_simplicity_budgets.py
npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict
git diff --check
```

Strict change validation was run before archival with `npx --yes @fission-ai/openspec@1.11.0 validate repair-five-dashboard-inventory-contracts --strict`.

## Pixels and preservation

Synthetic screenshots in [evidence](evidence): four original-source before images (Accounts and APIs at 1440/390px), plus ten current-source images (Accounts, selected sort, APIs detail/list and image picker at both widths). Reduced-motion captures wait for actual pie sectors. Desktop/mobile Accounts, compact APIs and image-picker pixels were inspected directly; no horizontal overflow was observed. Browser tests use intercepted fixtures, not real credentials or provider traffic.

Before work, 85 modified/untracked file contents were captured with SHA256 into `C:\Users\ext\AppData\Local\Temp\codex-five-ui-20261005-fp573fhv\baseline`, with manifest.json and source API snapshots alongside them. Final preservation evidence and batch file hashes are in [preservation.json](evidence/preservation.json). Existing locale values remain exact (2083 per language, 39 additive entries); prior api-keys context is a byte-identical prefix, and every prior api-keys requirement except the deliberately reconciled native filtering block remains exact. All other previous dirty files remain byte-identical.

## Boundaries

Final registry readback: all five selected rows explicitly state `ИСПРАВЛЕНО / ЗАКРЫТО ЛОКАЛЬНО`; the other 333 source rows remain byte-identical. Current source queue contains 338 records: 75 local closures, seven partial and 256 unverified. Final preservation readback confirms 79 of 85 previous dirty file contents byte-identical and six intended shared overlaps preserved as described above. Historical sections/counts remain historical snapshots.

This verifies the five local UI/API scopes. Broad PR #2065 is not closed; sibling records are not automatically marked verified. Real clients, hosted providers, distributed databases, full repository suite/aggregate stability, cloud CI/reviews, publication, release artifacts and production were not verified. Previous partial/public/cloud/platform residuals, F-045/CI-04 and F-082 retain their statuses. No commit, push, PR creation, merge, release or deploy was performed.
