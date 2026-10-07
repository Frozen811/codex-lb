# Five API-key and account quota contracts

Date: 2026-10-07 (UTC). Base: `ba4512387d71ba51cf1f6c27e0b5303364bcfa36`, fetched `origin/main`; local branch `main`. The user explicitly requested five unchecked registry tasks and a local main commit. No push, PR, merge, release or deployment is performed.

## Selected records and public sources

Exactly five previously `НЕ ПРОВЕРЕНО` rows: **UP-ISSUE-2492, UP-ISSUE-2556, UP-ISSUE-1080, UP-ISSUE-631, UP-PR-2463**. Original rows, issue bodies and the base SHA are in [source-snapshot.json](source-snapshot.json); current upstream PR metadata is in [pr-source.json](pr-source.json). Upstream closure or author claims do not substitute for local verification. PR 2463 remains open upstream; its maintainer/cloud approval gates are not changed here.

| Record | Finding and verified result |
| --- | --- |
| 2492 | Individual/bulk reset already existed, but partial failures lost the retry selection and showed only aggregate errors. Failed keys now retain selection and expose their names/errors. Public PATCH resets counters while preserving credential hash, identity, configuration and historical usage; the component test confirms the dialog names and a success/409 split. |
| 2556 | Traffic did not accrue credits, yet an exhausted legacy override rejected requests. The issue author accepts a documented display-only contract as an alternative to defined automatic conversion. Credits now explicitly remain display-only in the editor, translations and docs; compact traffic succeeds and token settlement still accrues 100,000 tokens. Existing `/v1/usage` credit values remain readable. |
| 1080 | Existing usage/trend endpoints supported longer periods but the dashboard always requested seven days. Detail queries now use the selected 7/30/60/90-day window, separate caches and matching labels. Lifetime inventory/overview labels stay explicit. Hook/component, frontend integration, real API endpoint tests and production browser requests verify the path. |
| 631 | The operator limit lived in a process-local dictionary. A nullable account column now persists it, both selection projections read it, and edits invalidate/publish routing changes. Real SQLite sessions and an already-created balancer verify zero, equality, clear and bypass behavior. Backup roundtrip preserves the cap; a legacy backup omitting the field leaves it unchanged. |
| 2463 | Existing estimated usage-share policy independently passes CRUD/strict validation, mixed capacity attribution, equality/rounding, missing/stale evidence and public subscription-route refusal checks. The HTTP regression proves 429 before dispatch and unchanged fixed-limit counters. No duplicate implementation or new attribution ledger is added. |

## Reproduction on the baseline

A detached worktree at the base SHA ran the same new API regression file, using the repository's isolated test database: **5 FAIL / 2 PASS**. Exhausted display-only credits produced HTTP 429; all three fresh account reads lacked the persisted quota field; backup export lacked `quotaLimitPercent`. Existing reset identity/history and live process-local restriction behavior passed. The final file passes all seven cases; the migration lifecycle adds one more case.

```bash
# Baseline worktree, with the new regression file copied into tests/integration
/workspace/codex-lb/.venv/bin/python -m pytest -q --tb=line --show-capture=no \
  tests/integration/test_key_quota_contracts.py
```

## Local verification

The broad backend selection passed **336 tests** before the additional backup-roundtrip test. The final new contracts/migration selection passed **8 tests**, overlapping seven cases from that broad run and adding one distinct case. After strengthening legacy-backup coverage, the changed case passed again. Total distinct verified backend cases: **337 PASS**, no skips. Repeated runs are not added to the total.

```bash
uv run --no-sync pytest -q --tb=line --show-capture=no -n 4 \
  tests/unit/test_api_keys_service.py tests/unit/test_api_keys_usage_windows.py \
  tests/unit/test_api_key_usage_share.py tests/unit/test_account_quota_restriction.py \
  tests/unit/test_account_backup_restore.py tests/integration/test_api_keys_api.py \
  tests/integration/test_api_keys_trends_api.py tests/integration/test_v1_usage.py \
  tests/integration/test_accounts_backup_and_quota.py \
  tests/integration/test_load_balancer_integration.py \
  tests/integration/test_key_quota_contracts.py \
  tests/integration/test_account_quota_limit_migration.py

uv run --no-sync pytest -q --tb=line --show-capture=no \
  tests/integration/test_key_quota_contracts.py \
  tests/integration/test_account_quota_limit_migration.py

uv run --no-sync pytest -q --tb=line --show-capture=no \
  tests/integration/test_key_quota_contracts.py::test_quota_limit_backup_restore_round_trip
```

Frontend feature/mocks selection: **188 PASS** across 23 files. After the cost-donut window label changed, the affected detail/donut suites passed **21 cases** again, already included in the feature selection. Updated full-page flow integration: **7 PASS**. Total distinct frontend cases: **195 PASS**.

```bash
cd frontend
node node_modules/vitest/vitest.mjs run \
  src/features/api-keys src/features/apis src/test/mocks/handler-coverage.test.ts
node node_modules/vitest/vitest.mjs run \
  src/features/apis/components/account-cost-donut.test.tsx \
  src/features/apis/components/api-detail.test.tsx
node node_modules/vitest/vitest.mjs run src/__integration__/apis-page-flow.test.tsx
node node_modules/@typescript/native/bin/tsc -b
node node_modules/vite/bin/vite.js build
```

Production-build Chromium checks: **2 PASS**, 1440px and 390px. Baseline capture: **2 PASS** separately, at the base SHA; those capture checks assert baseline controls rather than the new contracts. Both use repository-owned HTTP fixtures, with no provider traffic. Current checks assert `usage?days=30`, `trends?days=30`, matching labels and the display-only credit helper. Screenshots wait for chart loading, disable animations and show the credit helper within the dialog.

```bash
# Current production preview serves 4185; baseline preview serves 4186.
KEY_QUOTA_BASE_URL=http://127.0.0.1:4185 \
  KEY_QUOTA_EVIDENCE_DIR=/workspace/codex-lb/openspec/changes/repair-five-key-quota-contracts/evidence \
  node node_modules/@playwright/test/cli.js test --config browser-smoke/key-quota.config.ts
KEY_QUOTA_STAGE=before KEY_QUOTA_BASE_URL=http://127.0.0.1:4186 \
  KEY_QUOTA_EVIDENCE_DIR=/workspace/codex-lb/openspec/changes/repair-five-key-quota-contracts/evidence \
  node node_modules/@playwright/test/cli.js test --config browser-smoke/key-quota.config.ts
```

| Surface | Before | After |
| --- | --- | --- |
| Observation, desktop | [before](evidence/before-windows-1440.png) | [after](evidence/after-windows-1440.png) |
| Observation, mobile | [before](evidence/before-windows-390.png) | [after](evidence/after-windows-390.png) |
| Credit editor, desktop | [before](evidence/before-credits-1440.png) | [after](evidence/after-credits-1440.png) |
| Credit editor, mobile | [before](evidence/before-credits-390.png) | [after](evidence/after-credits-390.png) |

Additional gates: **PASS** for `make lint` (whole-repository Ruff, format1483, proxy/cancellation/timing, settings98/98 and migration topology272 with one head), scoped `ty check` on all eight changed production modules, scoped ESLint on all changed TypeScript files, TypeScript build, production build, simplicity budgets, strict MkDocs and whitespace. OpenSpec uses the CI-pinned version **1.11.0**: the change and **68/68 stable specs** validate strictly. The archive syncs five requirements / ten scenarios across two capabilities; stable contexts and rendered API-key docs are updated.

```bash
make lint
uv run --no-sync ty check app/core/balancer/logic.py app/db/models.py \
  app/modules/accounts/api.py app/modules/accounts/repository.py \
  app/modules/accounts/schemas.py app/modules/accounts/service.py \
  app/modules/api_keys/service.py app/modules/proxy/load_balancer.py
python .github/scripts/check_simplicity_budgets.py
uv run --frozen --group docs mkdocs build --strict -d /tmp/codex-key-quota-docs
npm exec --yes --package=@fission-ai/openspec@1.11.0 -- \
  openspec validate repair-five-key-quota-contracts --strict --no-interactive
npm exec --yes --package=@fission-ai/openspec@1.11.0 -- \
  openspec validate --specs --strict --no-interactive
git diff --check
```

## Registry preservation and boundaries

Only the five selected source rows change. The remaining **333/333 rows** match the base byte-for-byte; their sorted newline-joined SHA256 is `56d1efe519f7831dc3b9cc881699b9c9fd085c1dbef3428818aaa8365ccb02f0`. Current queue: **338 records —101 local closures, 7 partial, 230 НЕ ПРОВЕРЕНО**. Existing partials and external findings, including F-045/CI-04, retain their scope and status.

Tests use isolated SQLite and stubbed upstream/HTTP responses. A live multi-replica runtime, PostgreSQL/MySQL, actual provider credit conversion, new cloud CI, published artifacts and production are not certified. Known Starlette/AnyIO deprecation warnings remain. An exploratory `openspec validate --all` also covers unrelated active changes and reports 19 pre-existing active-change failures; the required stable-spec and selected-change validations pass. Unpinned OpenSpec1.14 adds strict length warnings to existing stable requirements, so the repository's CI-pinned validator is used.

The resulting local commit is identifiable without a self-referential SHA:

```bash
git log -1 --format=%H -- openspec/changes/archive/2026-10-07-repair-five-key-quota-contracts/verification.md
```
