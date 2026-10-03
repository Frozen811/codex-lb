# Python installation

Use Python 3.13 or newer. This fork keeps the distribution name `codex-lb`:
bare `pip install codex-lb` and `uvx codex-lb` select upstream PyPI. Select a
fork artifact URL or fork Git source explicitly. Docker source installs have
a separate [guide](docker.md).

## Historical release packages

The public `v1.25.0-hardened.3` wheel and sdist were checked on 2026-10-01.
Their metadata version is `1.25.1`, while runtime is `1.25.0-beta.9`; root
application code corresponds to the historical release, not newer checkout
fixes. Both install with working dashboard assets and migrations. The public
sdist also contains 5967 nested agent-worktree entries; prefer the wheel for
historical reproduction. No historical asset was replaced during the audit.

For an isolated pip environment on Windows (PowerShell):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl
.venv\Scripts\codex-lb.exe
```

On Linux/macOS:

```bash
python -m venv .venv
.venv/bin/python -m pip install https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl
.venv/bin/codex-lb
```

With uv, without activating a project environment:

```bash
uvx --python 3.13 --from https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl codex-lb
```

For a persistent uv tool install:

```bash
uv tool install --python 3.13 https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl
codex-lb
```

These commands deliberately select the historical wheel. A pinned old URL
does not become a newer release when refreshed. For updates, replace the URL
with the artifact you verified; `uv tool install --reinstall <artifact-url>`
replaces an existing tool source, including when package version metadata is
unchanged. See the [uv tool guide](https://docs.astral.sh/uv/guides/tools/).

## Install selected fork source

Choose an audited full commit SHA from the fork and replace `REPLACE_WITH_REVIEWED_FULL_SHA` below.
Install [Bun](https://bun.sh/docs/installation) **1.3.14**, matching
`frontend/package.json`, before building a source tree without dashboard assets:

```bash
bun --version  # must print 1.3.14
source_revision="REPLACE_WITH_REVIEWED_FULL_SHA"
[[ "$source_revision" =~ ^[0-9a-fA-F]{40}$ ]] || { echo "Select a reviewed full SHA first."; exit 1; }
uvx --python 3.13 --from "git+https://github.com/Frozen811/codex-lb.git@$source_revision" codex-lb
```

Windows PowerShell uses a different variable syntax:

```powershell
bun --version  # must print 1.3.14
$sourceRevision = "REPLACE_WITH_REVIEWED_FULL_SHA"
if ($sourceRevision -notmatch '^[0-9a-fA-F]{40}$') { throw "Select a reviewed full SHA first." }
uvx --python 3.13 --from "git+https://github.com/Frozen811/codex-lb.git@$sourceRevision" codex-lb
```

The package build hook runs `bun install --frozen-lockfile` and `bun run build`
when dashboard assets are absent. Missing/wrong Bun or an incomplete build
fails with prerequisite guidance. A complete release wheel or sdist already
contains assets and does not require Bun at install time. Source installation
needs network access for Python and frontend dependencies; build failure is
reported instead of producing a package whose dashboard is missing.

Editable development setup (`uv sync`) installs Python dependencies without
compiling the dashboard or requiring Bun. Build the frontend explicitly before
using its dashboard; this exception does not apply to distributable wheels/sdists.

For a checkout of the selected source, build distributable packages with
`uv build`, then install the wheel with `uv pip install --python <venv-python>
<wheel-path>` or pip. A source distribution can be installed the same way;
the corrected source distribution includes build helpers, frontend inputs and
assets, and excludes local dependencies/worktrees. The ordinary GitHub source
archive has no prebuilt assets and requires the pinned Bun prerequisite.

## Run from a fork checkout

Clone the fork and select the source revision you want to run. Source launchers
need [uv](https://docs.astral.sh/uv/) and Bun **1.3.14** on PATH. uv supplies a
compatible Python if one is unavailable. The launchers honor `uv.lock`, prepare
missing dashboard assets, and run from their own checkout even when invoked
from another directory. They do not install Bun automatically.

To install the pinned Bun with its official installer, use one of these
[version-specific commands](https://bun.sh/docs/installation#installing-older-versions),
then reopen the terminal and check `bun --version`:

```powershell
iex "& {$(irm https://bun.com/install.ps1)} -Version 1.3.14"
```

```bash
curl -fsSL https://bun.com/install | bash -s "bun-v1.3.14"
```

These optional setup commands install Bun in your user environment. The audit
used checksum-verified isolated binaries instead of changing the user's install.

```bash
git clone https://github.com/Frozen811/codex-lb.git || exit 1
cd codex-lb || exit 1
source_revision="REPLACE_WITH_REVIEWED_FULL_SHA"
[[ "$source_revision" =~ ^[0-9a-fA-F]{40}$ ]] || { echo "Select a reviewed full SHA first."; exit 1; }
git checkout --detach "$source_revision" || exit 1
```

Windows PowerShell:

```powershell
git clone https://github.com/Frozen811/codex-lb.git
if ($LASTEXITCODE -ne 0) { throw "Fork clone failed." }
Set-Location codex-lb
$sourceRevision = "REPLACE_WITH_REVIEWED_FULL_SHA"
if ($sourceRevision -notmatch '^[0-9a-fA-F]{40}$') { throw "Select a reviewed full SHA first." }
git checkout --detach $sourceRevision
if ($LASTEXITCODE -ne 0) { throw "Source selection failed." }
.\run.ps1
# Alternate port and a log path containing spaces:
.\run.ps1 --port 2547 --log-file "logs with spaces/server.log"
```

If script execution policy prevents that command, invoke it explicitly with
`powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run.ps1`. You can
also double-click `start.bat`; the batch wrapper delegates to the same launcher
and pauses after an interactive no-argument session ends. With explicit
arguments, it returns the CLI's status without requiring a key press.

Linux/WSL and macOS Bash, after selecting the checkout above:

```bash
./run.sh
./run.sh --port 2547 --log-file "logs with spaces/server.log"
```

The Git checkout preserves its executable bit. `./run.sh --help` and
`.\run.ps1 --help` work without frontend build prerequisites; normal startup
with missing assets fails clearly if Bun is absent or incompatible. Frontend
build tools are forced to use Bun, so an older host Node.js is not selected
by a Vite shebang, as described in the [Bun runtime guide](https://bun.sh/docs/runtime#--bun).

For manual development preparation: run `uv sync --dev --frozen`, then in
`frontend` run `bun install --frozen-lockfile` and `bun --bun run build`.
`uv run --frozen codex-lb` starts the CLI after that preparation. Editable
dependency setup alone does not build the dashboard. After changing frontend
sources or updating the checkout, rebuild the frontend explicitly; existing
complete assets are reused on subsequent launcher starts.

WSL uses Linux uv/Bun/Python inside its distribution. A Windows tool on PATH
is not a substitute for Linux dependencies. Keep its checkout/cache/data on
the Linux filesystem for reliable executable permissions and build behavior;
do not share one SQLite data directory with a simultaneously running Windows
instance. Default listeners are local; opening the service to a LAN requires
the [remote-access configuration](remote.md), not a launcher-specific firewall rule.

## Optional native transport helper

Basic source startup and the Python fallback do not require Rust. To build
the native transport helper, use the repository's pinned Rust **1.96.0** with
the platform linker/toolchain (MSVC Build Tools on Windows):

```bash
cargo build --release --locked --package codex-lb-egress-worker --bin codex-lb-native-egress
```

The application discovers `codex-lb-native-egress` through PATH. Add the
checkout's `target/release` directory for the current process before launching:

```powershell
$env:PATH = "$((Get-Location).Path)\target\release;$env:PATH"
.\run.ps1
```

```bash
PATH="$PWD/target/release:$PATH" ./run.sh
```

Use `codex-lb-native-egress --help` to verify the executable can run. This
does not prove real upstream transport or account routing. Prefer the tested
Docker source path when you want the helper and CA trust built into the image.

Windows PowerShell/cmd and Ubuntu 24.04 WSL launchers were exercised on paths
with spaces, foreign cwd, failures, readiness/assets and retained data. WSL
SIGTERM forwarding completed application shutdown and removed its listener;
uv returned signal status 143. macOS native startup remains an unexecuted
platform boundary rather than a claimed successful install.

## Startup and retained data

Open `http://localhost:2455` and check `/health/ready`. Both `codex-lb` and
`codex-lb-db` console scripts are installed; `codex-lb-db upgrade` and
`codex-lb-db check` expose migration diagnostics. Startup migrations use the
configured database. Optional external DB configuration follows [Database](../database.md).

Host installs default to `~/.codex-lb/` independent of the venv/tool directory;
`CODEX_LB_DATA_DIR` overrides it. Retain this directory and its encryption key,
back up the database before an update, and keep the same configuration when
recreating the tool environment. An isolated uv tool replacement passed data
and key retention checks. Do not run two writers against the same SQLite data.

Audit startup was verified on Windows/Python 3.13 in clean venvs outside the
checkout. Real account OAuth/Codex routing, macOS/Linux native installs and
custom enterprise network policies require separate checks. Package startup
does not prove that the fork's newer code is in a historical release.

## Update and rollback checks

Choose the fork URL/full source SHA or verified wheel explicitly. Stop the old
process and back up its DB/key/configuration before replacing the environment.
For `uv tool`, `uv tool install --reinstall <verified-fork-artifact-url>` replaces
the selected source even when package metadata has not changed; an old pinned
URL remains old when refreshed. Replacing a Python environment does not copy
data to another DB URL or preserve an independently configured key by itself.

For a checkout, check remote URLs before choosing the source, or fetch directly
from `https://github.com/Frozen811/codex-lb.git` at the reviewed full SHA. Save
local changes and use a clean/separate checkout. Rebuild changed frontend assets
with the pinned Bun/frozen lock. Run from the selected venv/tool and explicit
configuration, then check `import app; print(app.__version__)`, package/source
identity, migration state, readiness, assets, settings and account access.

For rollback, restore the old environment/executable with its matching
pre-upgrade DB/key snapshot in an isolated store first. Version metadata alone
does not establish schema compatibility. See the [Docker identity checks](docker.md#update-identity-and-rollback)
and [database backup guide](../database.md#backup-restore-and-rollback).

## Platform and topology evidence

The following is a **dated verification matrix**, not a guarantee for every
machine. The owning installation/runtime contracts remain in OpenSpec. Earlier
source/artifact snapshots and their limits are identified in the linked guide
sections and repository issues-check registry.

| Environment / target | Executed evidence | Boundary |
|---|---|---|
| Windows x64, Python 3.13 | Source PS5/pwsh/cmd launchers, wheel/tool startup, data/key retention; isolated Codex 0.159.3 HTTP/WS fixture on 2026-10-01/02 | Native console-close/Ctrl+C semantics, physical LAN/enterprise policies and real OpenAI login need separate runs |
| Linux/amd64 containers on Docker Desktop for Windows | Historical pinned public image, source/dependency overlay update + paired rollback, probes and Linux SIGTERM/SIGINT tests on 2026-10-02 | This is a Linux container runtime, not native macOS/Windows container support or every Linux host network setup |
| Ubuntu 24.04 WSL x86_64 | Prior 2026-10-01 source-launcher audit at published b5aa440b snapshot: Bun/uv, assets, paths, retained data, SIGTERM forwarding | WSL network-mode transitions and physical remote-client reachability remain unexecuted |
| Local kind/Kubernetes 1.35 amd64 | Prior 2026-10-02 chart install/upgrade, PostgreSQL/Secret retention and two-pod ring rehearsal | Declared minimum Kubernetes version, cloud/ESO/Ingress/Gateway/provider integrations are not all certified |
| Nix x86_64-linux | Prior 2026-10-02 package/dev-shell startup, assets/env/state and SIGTERM rehearsal | Flake declarations for aarch64-linux/aarch64-darwin are unexecuted runtime targets |
| Native macOS Intel/ARM64; Linux ARM64 | Command/build-target declarations only in this audit | No native runtime certification from these x64 runs |

The public fork OCI index observed on 2026-10-02 contains `linux/amd64` plus
`unknown/unknown` marked `attestation-manifest`. The attestation is metadata,
not an ARM64 runtime. A `py3-none-any` wheel describes Python packaging rather
than proving native dependencies/helper execution on every platform. A Nix
system declaration likewise needs its own build/runtime evidence. Choose a
path with evidence for your environment and verify new source/artifacts rather
than transferring an older green result to a different platform.

---

*Spec: [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation)*
