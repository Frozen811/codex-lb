# Tasks: Bump Dependencies (Batch 11)

- [x] Bump frontend dependencies per PR #2509 in `frontend/package.json` and `frontend/bun.lock`
- [x] Fix JSDOM 30.1.1 + Vitest 5.0.2 FormData compatibility in `frontend/src/test/setup.ts`
- [x] Fix TOTP dialog label association in `frontend/src/features/auth/components/totp-dialog.tsx`
- [x] Fix locale formatting in `thread-identity-card.tsx` and `model-catalogue-settings.tsx`
- [x] Add missing localization keys in `en.json`, `ko.json`, and `zh-CN.json`
- [x] Verify all 185 frontend test files pass (`bun run test`)
- [x] Verify frontend build (`bun run build`) and linter (`bun run lint`)
- [x] Bump Python package pins in `pyproject.toml` and lockfile in `uv.lock` per PR #2533
- [x] Verify Python linters (`uv run ruff check`) and migration topology (`scripts/check_migration_topology.py`)
- [x] Verify Python migration and unit test suites
- [x] Validate OpenSpec specifications (`bunx @fission-ai/openspec validate --specs`)
