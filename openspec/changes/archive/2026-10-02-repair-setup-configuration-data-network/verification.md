## Verification: repair-setup-configuration-data-network

Date: 2026-10-02. Base HEAD: f52adb7274c96c0702e19aa02eabd4f1c7556231. Local uncommitted delta; existing changes preserved.

## Completeness

All seven implementation/verification tasks complete. Four added requirements and six scenarios are synchronized with the two owning main specs. Operator guides link to those specs. No new dependency, setting field, schema revision or budget increase.

## Correctness mapping

| Requirement / scenario | Implementation and evidence |
|---|---|
| Configuration discovery / package outside source | docs/configuration.md + .env.example; test_settings_env_files.py fresh interpreters cover root/cwd, missing/blank explicit paths, ordered relative files, process override and ignored listener/unknown dotenv names; test_settings_home_dir.py preserves dependent data paths; prior Nix/Helm runtime §22 retained |
| Dashboard persistence / env fallback | test_setup_process.py actual CLI HTTP PUT/GET and restart; test_settings_api.py 146-test subsystem batch; source-mounted PostgreSQL/MySQL runtime: 9 remains effective against changed 6/7 env and clearing returns to 7 |
| Invalid keep-alive / negative flag or env | app/cli.py lower bound; test_cli.py negative flag/env before server seam, zero valid; test_setup_process.py fresh command exits without creating store; before fix 2 failed / 1 passed |
| Paired backup / recreate or restore | docs/database.md + Docker storage caveat; fresh CLI SQLite backup/restore HTTP/account/decrypt/fingerprint guard regression; actual PostgreSQL custom dump/import and MySQL logical dump/import to empty isolated DBs; all three schema checks migration_policy=ok/schema_drift=none; Unix UID1000/key0600 and unwritable-storage refusal |
| Endpoint matrix / external DB | docs/deployment/remote.md; source runtime on bridge reaches sibling PostgreSQL/MySQL by service DNS; Docker Desktop host.docker.internal reaches disposable host listener; container/host HTTP readiness and host mapping independently observed |
| Endpoint matrix / remote client contract | docs separate bind 0.0.0.0 from client server-name, published HTTP port from login-only callback 1455, and WSL/Linux prerequisites; actual host-published readiness, container callback absent before login and two port-collision refusals; physical LAN/WSL/Linux-host paths explicitly unexecuted |

The documented SQLite Python backup snippet itself passed with a committed WAL row and rejected an existing destination. PostgreSQL/MySQL runtime used current source mounted over a prior image's dependency environment, not a newly published image. Restart/restore reads retained synthetic paused account ciphertext without printing credential values. Docker SIGTERM finished gracefully; Windows process termination is recorded as crash-style.

## Coherence and checks

- Focused pytest: 55 CLI/env/home + 146 settings/API/networking + 3 fresh process tests = **204 passed**, no skips; existing Starlette/AnyIO warning.
- Full Ruff check and format check: PASS, 1424 files. Full ty: PASS. All five architecture checks: PASS.
- Simplicity budgets: README222/225, headings10/10, env54/60, nav5/5, root0/0, settings98/98; no threshold changes.
- Strict MkDocs build: PASS, including backup and endpoint cross-links.
- OpenSpec 1.11.0 strict change + 68 main capabilities: PASS.
- Code-navigation graph located existing CLI/env resolver and direct main caller; dynamic Pydantic resolution/framework/environment behavior verified in current source and fresh interpreters. Graph has no substitute for process/environment tests.

## Limits and disposition

No critical implementation issue or spec divergence remains. The delivered local change is ready for archive. SETUP-04 remains partially open in issues-check for physical LAN/WSL/Linux host networking and actual network switching; guide accuracy is verified without asserting those platform runs. Real OAuth, upstream credential use, TLS/SSE/WebSocket qualification, public packages/images, cloud CI and older-binary downgrade remain separate evidence. Archive does not close those audit items.

Temporary runtime evidence: C:/Users/ext/AppData/Local/Temp/codex-setup-20261002/report.json and network-report.json. These are local rehearsal files, not release artifacts; reproducible SQLite/CLI regressions are committed-source test files. All rehearsal Docker containers/volumes/networks were removed; the pre-existing application container remains running.
