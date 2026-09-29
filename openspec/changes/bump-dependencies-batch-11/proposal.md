# Bump Frontend & Python minor-patch dependencies (Batch 11)

## Why

Dependabot proposed dependency updates for frontend and python packages in PR #2509 and PR #2533:
1. PR #2509: 16 frontend minor and patch updates (Vite 8.3.1, Vitest 5.0.2, JSDOM 30.1.1, React Query 5.103.2, Lucide React 1.48.0, TypeScript-ESLint 8.70.1, React-i18next 17.0.15, etc.).
2. PR #2533: 17 python minor and patch updates (Alembic 1.20.0, SQLAlchemy 2.1.1, OpenTelemetry 1.45.0/0.66b0, Ruff 0.16.9, Uvicorn 0.54.0, Ty 0.0.84, OpenAI 3.20.0, Hatchling 1.32.4, etc.).

Upgrading these dependencies requires resolving test environment incompatibilities:
- JSDOM 30.1.1 private symbol `#impl` incompatibility with Vitest's Request wrapper when handling `FormData` with `File`/`Blob`.
- OTP form input `htmlFor="totp-code"` association in `totp-dialog.tsx`.
- Locales number formatting independence (`en-US`).
- Missing localization keys in `en.json`, `ko.json`, and `zh-CN.json`.

## What Changes

1. Bump `frontend/package.json` dependencies and update `frontend/bun.lock`.
2. Adapt `frontend/src/test/setup.ts` to unwrap Vitest's Request wrapper and ensure `FormData`/`File`/`Blob` compatibility.
3. Update `totp-dialog.tsx` to explicitly associate `htmlFor="totp-code"`.
4. Fix number formatting in `thread-identity-card.tsx` and `model-catalogue-settings.tsx`.
5. Add missing i18n keys across English, Korean, and Simplified Chinese locale bundles.
6. Bump Python pins in `pyproject.toml` (`ty==0.0.84`, `hatchling==1.32.4`) and upgrade packages in `uv.lock`.
7. Rebuild frontend production assets and verify 100% test pass rate across frontend and backend.
