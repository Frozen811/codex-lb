# Nix installation

Run from a checkout of [Frozen811/codex-lb](https://github.com/Frozen811/codex-lb).
Commands on this page use Linux/WSL/macOS **Bash**, not PowerShell.
Nix needs the `nix-command` and `flakes` experimental features enabled. The
flake builds the Python package and dashboard with its locked inputs; it does
not need the checkout's `.venv`, Bun installation or `app/static` directory.

```bash
git clone https://github.com/Frozen811/codex-lb.git
cd codex-lb
nix build .
mkdir -p "$HOME/.codex-lb"
export CODEX_LB_DATA_DIR="$HOME/.codex-lb"
nix run . -- --host 127.0.0.1 --port 2455
```

Open [localhost:2455](http://localhost:2455) and check `/health/ready`.
Keep the data directory, database and `encryption.key` together across restarts
and upgrades. Never place writable state inside `/nix/store`.

## Run outside the checkout

After `nix build .`, resolve the `result` symlink and run its executable from
your chosen launch directory:

```bash
package=$(readlink -f result)
mkdir -p "$HOME/codex-lb-launch"
cd "$HOME/codex-lb-launch"
CODEX_LB_DATA_DIR="$HOME/.codex-lb" "$package/bin/codex-lb" --host 127.0.0.1
```

The Nix wrappers load `.env` followed by `.env.local` from the launch directory.
An explicit `CODEX_LB_ENV_FILE` wins; environment values override env-file
values. Relative paths in those files resolve from the launch directory.
Avoid printing env files or bootstrap tokens into shared logs.

For a remote source pin, replace `FULL_COMMIT_SHA` with the full revision you
have selected and verified:

```bash
nix run github:Frozen811/codex-lb/FULL_COMMIT_SHA -- --host 127.0.0.1
```

`github:Soju06/codex-lb` selects upstream. The unpinned fork URL follows its
default branch and does not guarantee a particular audit or release revision.

## Update and platform coverage

Stop the running process, back up the database and matching key, select the
new source revision, rebuild and restart with the same data directory. A Nix
package rollback does not downgrade a migrated database: restore a compatible
database/key backup before starting older code. Review the
[Kubernetes migration ordering notes](kubernetes.md) when crossing destructive
schema changes; the same old-process drain requirement applies here.

The flake declares x86_64 Linux, aarch64 Linux and aarch64 Darwin. Installation
and startup were exercised on x86_64 Linux; the other systems need their own
runtime verification. Windows requires a Linux Nix environment such as WSL,
with its own paths and storage. The optional Rust native egress helper is not
built by this flake; the packaged default uses the supported Python transport.
Real OAuth/Codex requests require account setup and are separate from package
readiness. `nix develop` provides editable Python dependencies; build dashboard
assets explicitly as described in the [Python guide](python.md).

Contract: [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation).
