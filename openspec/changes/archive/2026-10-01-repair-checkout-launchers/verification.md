# Verification — checkout launchers

Eight implementation tasks complete for INSTALL-09/10/11. macOS native execution is explicitly unverified. Main integration of the preceding audited changes is recorded separately in issues-check.md §21.

## Product-path coverage

- Baseline clean source: backend ready, dashboard 503; Windows native CLI failure returned wrapper zero.
- Fresh Windows PowerShell 5/pwsh/cmd sources from foreign cwd and paths with spaces passed actual readiness, HTML/JS/CSS, log-path argument forwarding and data/key reuse.
- Help avoids frontend compilation; missing uv/wrong Bun and invalid CLI argument paths preserve nonzero status. Source helper tests cover delegation/preparation/args/failure semantics.
- Ubuntu 24.04 WSL fresh no-asset source passed pinned Bun build, direct executable Bash startup, foreign cwd/args/spaces, repeated data/key retention and SIGTERM application shutdown with no surviving listener. uv signal return 143 is expected, not forced to zero.
- Linux host Node 18.19.1 broke the Vite shebang path; forced Bun runtime fixed it and passed actual builds on both Windows and Linux.
- Optional Windows Rust 1.96.0 helper build used isolated cargo directories and passed executable help, PATH discovery, protocol handshake and process cleanup.

## Coherence/checks

Normative requirement is synced to deployment-installation, narrative decisions/failure modes in context, user instructions in the linked Python guide. No new runtime setting, dependency floor or README heading; existing source prerequisites are explicit. Thirty-five focused tests passed, with one existing Starlette warning. Full Ruff/format/ty, architecture, simplicity and strict 68 specs passed. Bash Git mode is 100755.

## Boundaries

No real accounts/OAuth/Codex, native macOS, production/LAN firewall or graceful Windows GUI-console-close proof. Test processes were stopped; disposable downloads/cache/source/data retained. A policy rejection prevented one test-directory cleanup; another clean copy completed the final smoke without repeating deletion. Intermediate harness failures and the old-host-Node defect are recorded in issues-check.md §21 rather than counted as successes.

This local source verification does not assert that the new launcher branch has completed cloud CI or been merged into main. Publication follows the focused branch/PR workflow and release/image publication remains separate.
