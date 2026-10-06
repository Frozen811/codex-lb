## Design and operational tradeoffs

File scheduling keeps each module's session-loop and global-state assumptions
serial while allowing independent modules to overlap. The controller provisions
server databases before workers import the application and owns their cleanup,
including worker crashes. PostgreSQL uses force-drop after the session; MySQL
grants are limited to the disposable test namespace. Multi-session commits and
DDL remain real: a blanket rollback fixture would hide commit/durability bugs
and cannot roll back MySQL DDL. Existing per-file MySQL schema resets are kept.

SQLite uses a unique temporary directory per process, on writable `/dev/shm`
where available. Disk files preserve cross-connection and subprocess behavior
that `:memory:` would change. Encryption keys use the same isolated directory.
Auto concurrency observes process CPU availability, Linux cgroup quotas, and
available physical memory (including Windows GlobalMemoryStatusEx).
Parallel file assignment exposed an existing ambient request ID leak in native
stream golden checks. An autouse fixture now scopes request and request-scope
ContextVars to each test, preserving middleware behavior while removing dependence
on which file ran previously. The related native/request-context checks pass
with two workers (55 tests).

Vitest thread workers retain per-file isolation. MSW handlers and mutable mock
state reset after unmounting, timers return to real time, and storage/global/env
stubs are cleared. An existing multipart import regression came from jsdom
FormData being encoded as text/plain by a Node Request. Undici request/form-data
constructors plus node:buffer File/Blob keep this test boundary consistent. The
account import scenario now verifies actual uploaded filenames, rather than
fabricating them from request order.
Undici is loaded dynamically after installing node:buffer Blob/File, because
its WebIDL module captures the Blob constructor during import. A dedicated MSW
multipart regression verifies the filename and file contents, and the pasted
token dialog test uses the standard File.text() API rather than jsdom FileReader.
The account flow also waits for Radix's modal layer to accept pointer events
before uploading. Finding the input alone is insufficient: the layer registers
on the next frame, producing a load-dependent pointer-events failure.

The dashboard producer runs for either contract side; pytest consumers retain
always-running placeholder contexts even when the producer is skipped. Artifact
downloads refer to this workflow run only. Local asset reuse hashes build inputs
and validates HTML/JS/CSS completeness; an explicit CI artifact flag validates
completeness and never silently compiles source. UV caches use the locked Python
dependency input. Bun's frozen install remains cheap when dependencies match.
The local source digest includes public assets as well as source/configuration
files, so a changed font or favicon invalidates the cached build.

Six deterministic integration shards use estimated seconds for new files,
including parametrization, DB fixture overhead, DDL and explicit waits. JUnit
reports can refresh a shared duration snapshot; reports from server-database
slices should not be mixed into SQLite integration-core history. Shard verification
checks completeness and disjointness, and invalid duration values fail early.

## Test stack and commands

Backend tests are Python/pytest with pytest-asyncio, Hypothesis and pytest-xdist,
running against the FastAPI ASGI application. Frontend tests are TypeScript/React
with Vitest, jsdom, Testing Library and MSW; real browser checks use Playwright.
Dependency inputs are `pyproject.toml`/`uv.lock` and `frontend/package.json`/`bun.lock`.

CI runs on pushes to `main`, pull-request source updates (`opened`, `reopened`,
`synchronize`, `ready_for_review`) and `merge_group`. Area detection controls
expensive steps while retaining required pytest check contexts. The Windows
workflow additionally supports manual dispatch.

Linux Make targets include `make test-unit`, `make test-integration-core`,
`make test-integration-bridge`, `make test-e2e` and `make frontend-test-fast`.
Direct commands below also work in PowerShell; `--ignore`, `-m`, `-k` and explicit
file/node IDs select subsets, while `-n 0` disables worker parallelism.

```powershell
uv sync --dev --frozen
uv run --no-project python -m scripts.build_test_dashboard
uv run --no-sync pytest -n auto --dist=loadfile tests/unit tests/simulation tests/test_request_logs_options_api.py
uv run --no-sync pytest -n auto --dist=loadfile tests/integration --ignore=tests/integration/test_http_responses_bridge.py --ignore=tests/integration/test_proxy_websocket_responses.py
uv run --no-sync python .github/scripts/pytest_shards.py --shard-count 6 --verify
```

Frontend commands are also cross-platform:

```powershell
cd frontend
bun install --frozen-lockfile
bun run test
```

## Changed files

- `Makefile`, `pyproject.toml`: file-level parallelism, bounded diagnostics,
  artifact validation/build reuse, six shard targets and optional JUnit reports.
- `tests/runtime.py`, `tests/conftest.py`: worker storage and server-database
  lifecycle, cross-platform resource limits, Hypothesis profiles and ContextVar isolation.
- `tests/unit/test_test_runtime.py`, `tests/unit/test_pytest_shards.py`,
  `tests/unit/test_ci_workflow_required_checks.py`: spawn/isolation, weighted
  partitioning and required-check/artifact regressions.
- `frontend/vite.config.ts`, `frontend/src/test/setup.ts`: isolated threads,
  bounded concurrency, mock cleanup and consistent multipart constructors.
- `frontend/package.json`, `frontend/bun.lock`: locked Undici test dependency.
- `frontend/src/test/multipart.test.ts`,
  `frontend/src/__integration__/accounts-flow.test.tsx`,
  `frontend/src/features/accounts/components/import-dialog.test.tsx`: multipart
  regression, real filename checks, modal readiness and native File.text().
- `.github/scripts/pytest_shards.py`, `.github/workflows/ci.yml`,
  `.github/workflows/windows-startup.yml`: weighted six-shard CI, one shared
  dashboard artifact for test/package consumers, cache inputs, isolated MySQL
  permissions and PowerShell spawn coverage.
- `scripts/build_test_dashboard.py`, `.gitignore`, `.github/CONTRIBUTING.md`:
  source/public asset caching, report directory ignore and platform commands.
- OpenSpec proposal, tasks, delta requirements and context: test runtime contract
  and verification evidence; canonical github-automation documentation is synced
  when the verified change is archived.

## Verification

Measurements use this Linux environment with a two-CPU cgroup quota, warm package
caches and shell wall-clock timing. Initial baselines were run before edits:
unit took 526.928 seconds (nine failures due to absent Helm), and frontend took
545.097 seconds (one existing multipart import failure). Helm 3.19 and locked
chart dependencies were subsequently provided in the execution environment.
These failing baselines are useful timing observations, not passing performance
gates; the new unit run includes additional infrastructure and Helm checks.
The unit CI slice now explicitly sets up the tested Helm 3.19.0 version instead
of relying on whichever Helm is bundled in the runner image.

- Parallel infrastructure/CI regression checks: 22 passed with two workers.
- Required-check regression checks after pinning Helm: 10 passed.
- Spawn ASGI probe: child inherits the parent's database URL and serves /health.
- Explicit Hypothesis profiles: 4 property tests passed with `ci` (50 examples
  each), and 1 passed with `thorough` (500 examples), confirmed by statistics.
- PostgreSQL 16 isolation: 36 passed with two workers; no worker databases remained.
- MySQL 8.4 isolation: 28 passed, 8 PostgreSQL-only checks skipped; no worker databases remained.
- Full SQLite integration-core: 4,549 passed, 440 skipped in 2,132.99 seconds.
  Skips cover server-specific assertions, optional metrics dependencies and native
  binary probes; the separate server checks above cover the database isolation path.
- Full SQLite integration-bridge: 439 passed in 289.26 seconds.
- Full e2e: 27 passed, 1 optional installed-Codex check skipped in 21.67 seconds.
- Helm startup checks after tool setup: 21 passed.
- Focused multipart and account import frontend checks: 11 passed using thread workers.
- Account-flow stress checks: three repeated runs passed (9 tests) while the
  SQLite integration suite consumed the same two-CPU quota.
- Dashboard cache: repeated `make frontend-ready` reused the build; modifying a
  public asset changed its source digest.
- Sharding: all 209 integration-core files partitioned once into six nonempty shards.
- Full `make lint typecheck` and frontend lint/type checks passed.
- OpenSpec: strict change validation and all 68 canonical specifications passed.

Full unit verification: `make test-unit` passed with 12,656 passed, 7 skipped,
1 expected failure and no failures in 290.34 seconds of pytest time. Including
build/setup, wall-clock was 310.240 seconds versus the initial 526.928 seconds
(1.70x faster). This environment limits CPU execution to two cores, and the
baseline skipped Helm-dependent checks that the passing run executes.
Full frontend verification: `make frontend-test-fast` passed with 190 files and
1,745 tests in 299.96 seconds of Vitest time. Wall-clock was 300.479 seconds versus
the initial 545.097 seconds (1.81x faster). The baseline's multipart failure is
fixed, and the passing run includes an additional multipart regression test.

| Command | Initial wall-clock | Final wall-clock | Observed speedup |
| --- | ---: | ---: | ---: |
| `make test-unit` | 526.928 s | 310.240 s | 1.70x |
| `make frontend-test-fast` | 545.097 s | 300.479 s | 1.81x |

Full unit and frontend measurements were separate. Focused frontend diagnostics
overlapped part of unit setup; the final frontend timing ran without backend or
stress suites. These are observed development timings, not controlled performance
gates. Raw Linux
logs are `/tmp/codex-lb-unit-before.log`, `/tmp/codex-lb-unit-after-final.log`,
`/tmp/codex-lb-frontend-before.log`, and `/tmp/codex-lb-frontend-after-passed.log`;
their adjacent `.time` files contain shell `real`, `user`, and `sys` measurements.
The actual CI critical path depends on runner resources and job concurrency;
the requested 2–4x cloud speedup has not been measured in this workspace.

Actual GitHub Actions wall-clock speedup and execution on a Windows machine
require their respective CI runs; Linux spawn coverage does not substitute for
a Windows host measurement. No universal absence of future flakes is inferred
from successful test runs.
