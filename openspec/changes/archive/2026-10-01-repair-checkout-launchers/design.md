## Decisions

Use one Python source-start helper under scripts to reuse pinned dashboard preparation and delegate to app.cli in the same interpreter. PowerShell changes to PSScriptRoot and preserves the CLI result; batch delegates to PowerShell rather than duplicating prerequisites and restores the CLI error after an interactive pause. Bash resolves its own directory and execs uv to preserve signals/exit status.

Use uv run --frozen so launchers honor the project lock. Skip dashboard preparation for help flags only; normal startup must provide working dashboard assets. Do not auto-install Bun/Rust or change account configuration. The optional native helper remains discoverable through runtime PATH and is documented with pinned Rust and platform prerequisites.

Linux source startup exposed an old-host-Node trap: Bun's build script launched Vite via its node shebang and selected Node 18, which lacks node:util styleText. Dashboard preparation now forces the pinned Bun runtime with --bun, keeping the documented source prerequisite sufficient. SIGTERM is forwarded through uv; a supervisor exit 143 with complete application shutdown and no listener is expected signal semantics, not a failed graceful stop.

## Verification

Run scripts from outside copies whose paths contain spaces, with isolated cache/venv/data/key/SQLite and loopback ports. Test missing uv/Bun, incompatible Bun, bad CLI arguments and preserved failure status. Reproduce baseline behavior first, then validate readiness/assets, argument forwarding, persistence and cleanup. Use real Windows PowerShell/cmd and Linux WSL; document macOS as an unexecuted platform boundary.
