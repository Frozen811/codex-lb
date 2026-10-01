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

Choose an audited commit SHA from the fork and replace `<source-sha>` below.
Install [Bun](https://bun.sh/docs/installation) **1.3.14**, matching
`frontend/package.json`, before building a source tree without dashboard assets:

```bash
bun --version  # must print 1.3.14
uvx --python 3.13 --from git+https://github.com/Frozen811/codex-lb.git@<source-sha> codex-lb
```

The package build hook runs `bun install --frozen-lockfile` and `bun run build`
when dashboard assets are absent. Missing/wrong Bun or an incomplete build
fails with prerequisite guidance. A complete release wheel or sdist already
contains assets and does not require Bun at install time. Source installation
needs network access for Python and frontend dependencies; build failure is
reported instead of producing a package whose dashboard is missing.

For a checkout of the selected source, build distributable packages with
`uv build`, then install the wheel with `uv pip install --python <venv-python>
<wheel-path>` or pip. A source distribution can be installed the same way;
the corrected source distribution includes build helpers, frontend inputs and
assets, and excludes local dependencies/worktrees. The ordinary GitHub source
archive has no prebuilt assets and requires the pinned Bun prerequisite.

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

---

*Spec: [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation)*
