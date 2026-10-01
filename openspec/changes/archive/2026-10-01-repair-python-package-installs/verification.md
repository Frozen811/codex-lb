# Verification — repair-python-package-installs

All eight tasks complete. INSTALL-06/07/08 runtime coverage is Windows/Python 3.13.12; source publication is fork branch fix/python-install-audit, immutable package source 4395926017cc688fe8c3cc48a308d667941bd17d. No public artifact/release replacement or main merge.

## Requirement coverage

| Requirement | Product-path evidence |
|---|---|
| Complete source-wheel dashboard | Baseline clean snapshot built a dashboard-less wheel. Fixed PEP 517 build used checksum-verified Bun 1.3.14/frozen lock and installed dashboard readiness/assets. Published exact-SHA Git uvx install outside repo independently passed. |
| Fail-closed prerequisites/output | Actual wrong Bun 1.4.2 rejected package before wheel emission. Eleven regressions cover absent/wrong Bun, missing/empty/escaping assets, install/build failures, incomplete output, pinned frozen build and prebuilt reuse. |
| Sdist contains required inputs without workstation state | Actual root and nested marker probes; four nested leaks reproduced and all markers absent after explicit excludes. Build helpers ship, complete sdist rebuild/install works with incompatible host Bun because it reuses assets. |
| Known fork versus upstream channel | Public assets re-downloaded; metadata/runtime disclosed. 762 Python files match tag deed76ba after newline normalization; wheel and sdist root code equal bytewise. README/translations/guide explicitly select fork wheel or selected source SHA. |
| Installed readiness/migrations/data/update | Actual pip, uv pip, uvx and uv tool installs outside checkout passed CLI/migration console/schema/readiness/HTML/JS/CSS. Isolated tool source replacement retained synthetic setting/key; remote Git source install also passed. |

## Coherence and checks

- Requirements synced into deployment-installation; rationale/examples/failure modes in owning context; rendered Python page linked to spec and nav.
- No new runtime setting or application dependency. Hatchling remains isolated build dependency. Existing pinned packageManager owns Bun version.
- 1628 unit + 388 HTTP/WebSocket/quarantine route tests passed, 2016 unique tests; existing Starlette deprecation warning. Repeat hook tests not double counted.
- Repository-wide Ruff check/format and ty check passed. Four existing format-only files normalized in a separate commit, AST unchanged.
- Architecture, simplicity, lock, actionlint and git diff checks passed; strict change + 68 main specs passed.
- Source fixes committed by concern and pushed; exact remote SHA confirmed. Main/PR/merge_group CI does not trigger for this branch push, so no full green cloud CI claim. Windows diagnostic dispatch is separate post-publication evidence and cannot satisfy exact-source main-push release gates.

## Boundaries

Historical artifact version drift/worktree leak remains in public hardened.3. No real accounts, OAuth/Codex, enterprise network, native Linux/macOS or downgrade proof. No full make ci on this Windows host; no local make executable. Intermediate uvx identity probe imported checkout app; outside cwd/python -I corrected that harness failure. All smoke process trees stopped, isolated tool install removed; temporary downloads/venvs/cache retained.

Detailed hashes, commands, installation facts, commits and remaining work are in issues-check.md §20. No unresolved implementation requirements within this scoped change.
