# Deployment & Installation Context

## Purpose and Scope

This capability owns the install contracts (Helm modes, Compose profiles,
smoke tests) and the operator environment-variable contract at
settings-load time: which `CODEX_LB_*` values exist, which are deliberately
fixed, and how removed settings are retired.

See `openspec/specs/deployment-installation/spec.md` for normative
requirements.

## Local Docker, development Compose and distroless

The fork source-build path uses the selected Frozen811/codex-lb checkout. Standard and distroless builds compile frontend and native helper with frozen Bun/uv/Cargo locks; all frontend container targets use the package's pinned Bun 1.3.14. Root and frontend Docker contexts exclude workstation dependency trees, nested env/credential files, databases and agent worktrees. A synthetic BuildKit COPY/export test reproduced the old context leaks and verified the exclusions without copying real secrets.

Named volumes initialize the correct ownership for standard UID/GID 1000 and distroless UID/GID 65532. Both images use shell-independent Python readiness healthchecks. Their CLI startup, dashboard HTML/JS/CSS, CA trust and native helper were checked in Linux/amd64 containers on Docker Desktop for Windows. Recreating each image with the same isolated named volume preserved a changed dashboard setting and encryption-key hash; graceful stop exited zero. These are source-built artifacts, not proof about public tags, ARM64 or real Codex routing. Bind mounts require matching operator-managed permissions; downgrading an image across a database migration needs an explicit compatibility plan.

The root Compose file is development tooling: backend at 2455, OAuth callback at 1455 and Vite at 5173. No env file is required. Its optional env-file syntax needs [Compose 2.24.0 or later](https://docs.docker.com/reference/compose-file/services/#required). The frontend uses UID 1000 (`bun`) with owned writable source/dependency cache paths; the previous inline target inherited root. Vite resolves `server:2455` on the service network. Source watch restarts backend and syncs frontend while excluding frontend env/dependencies. Example: opening `/health/ready` through port 5173 verifies the frontend-to-backend proxy; merely receiving Vite HTML does not establish that connection.

The stock named volumes have explicit names; changing `-p` alone cannot isolate data. Audit stands override every volume name and bind random ports only on loopback. Watch sync becomes visible before backend restart finishes, and Docker can reassign an ephemeral published port on restart, so probes must observe the new start and re-resolve the port. On Windows, terminating the docker launcher alone can leave the Compose watch child alive; terminate the owned process tree in automated audit cleanup. Ordinary interactive users can stop watch with Ctrl+C.

Docker CI now builds standard and distroless images and uses isolated tmpfs-backed containers for readiness/assets/native/CA checks, with failure cleanup. Local validation of this workflow does not assert that it ran on GitHub; the existing standard-image Trivy checks remain separate from installation smoke. Distroless has no shell: diagnose with container logs and Python. See [rendered Docker guidance](../../../docs/deployment/docker.md).

## Fork public images and server-only Compose

The 2026-10-01 anonymous registry check resolves `latest` and `1.25.1` to index digest `sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447`, source `f622c5632013d24ce9236d176113087b387c7990`. OCI version is `1.25.1` while runtime is `1.25.0-beta.9`. The historical image copies source without installing the project distribution, so installed `codex-lb` package metadata is absent; package-version APIs must not be assumed available. Runtime platform is linux/amd64; unknown/unknown is attestation metadata. That digest passed anonymous pull, named-bridge readiness/assets and non-root named-volume recreation, but contains no built-in Docker HEALTHCHECK and does not contain later checkout fixes. No public tags were changed. Use a source build for the selected checkout, or deliberately select a verified public artifact; installation smoke is not real-account routing evidence.

Previously server-only Compose declared both `build` and `ghcr.io/frozen811/codex-lb:1.25.1`. Ordinary `up` chose the cached historical image. It now uses a local `codex-lb:local` name and `pull_policy: build`, keeping source installation separate from release identity. A test seeded the audit's local tag with the historical image and proved normal startup replaces it with matching checkout source. No env file means SQLite. External PostgreSQL remains optional; the application data volume still contains the encryption key and must be retained with the database backup. Named volumes retain the stock fixed names for compatibility, so separate instances must override them as well as ports.

Example: `.env.local` with `CODEX_LB_DATABASE_URL=postgresql+asyncpg://codex_lb:codex_lb@postgres:5432/codex_lb` selects the development PostgreSQL service. A host client instead uses `127.0.0.1:5432`; localhost inside the application is the application container, not the database. Profiles start databases only and do not infer a backend. Start the selected DB with `up -d --wait`, then recreate the backend to load env changes. Enabling both profiles does not combine their databases. Fixed profile passwords are development fixtures, not production credentials.

Availability-only probes did not establish DB access: MySQL `mysqladmin ping` accepted a wrong password, PostgreSQL `pg_isready` accepted a nonexistent user/database, and initdb's loopback trust rules accepted a wrong password even in a real SQL query. Profiles now execute SQL as the configured app user against its database; PostgreSQL connects through `$HOSTNAME` to use network authentication. Tests reject wrong passwords and missing databases and verify actual schema migrations, remote settings, key retention and readiness after app recreation. Existing volumes whose operator explicitly chose trust authentication still follow that authentication policy; a health probe cannot impose a server password policy.

External PostgreSQL with verified TLS was rehearsed with `PGSSLMODE=verify-full` and `PGSSLROOTCERT` pointing at a read-only mounted CA certificate. These existing driver variables apply to both psycopg migrations and asyncpg runtime without competing URL query semantics or new application settings. Startup and schema check, SQL `pg_stat_ssl`, app recreation, PostgreSQL dump/restore into another database with the original application key, and database container recreation/reconnection passed. Invalid passwords, DNS, certificate hostnames and untrusted CA configuration are tested as fail-before-readiness paths. An operator's actual remote network and certificate chain remain deployment-specific.

The pinned postgres-upgrade helper also passed an offline synthetic PostgreSQL 16 в†’ 18 rehearsal: a volume-root legacy layout was refused by the ordinary 18 service, an offline tar backup was readable, the one-shot helper upgraded the data, and PostgreSQL 18.6 retained the synthetic row. This is not a production-size rehearsal, a restore test of that tar archive, or proof for all alternative volume layouts. See [Docker](../../../docs/deployment/docker.md) and [Database](../../../docs/database.md) for installation commands. Public alias repair remains release-gated, and local edits have not run in cloud CI.

## Python package and Git installation channels

The fork's distribution name remains codex-lb, so bare index commands select upstream. Python installation guidance uses an explicit fork wheel URL or selected Git commit. The historical hardened.3 wheel and sdist both carry metadata 1.25.1 and runtime 1.25.0-beta.9. All 762 root application Python files match tag deed76bab5fafa36051c2cf474a1b29055988aae after CRLF/LF normalization; raw byte differences are not code drift. The public sdist contains 5967 nested .kilo/worktrees entries and is historical; no existing release asset was replaced. Both public artifacts passed clean Windows/Python 3.13 CLI, migrations/schema-check, readiness and dashboard startup outside the checkout.

Previously Git source installs silently built a wheel without the ignored app/static directory. The custom Hatch build hook now checks HTML-referenced JavaScript/CSS and invokes the frontend's exact Bun 1.3.14 with a frozen lock if assets are missing. Missing or incompatible Bun fails with prerequisite guidance; failed frontend processes or incomplete output fail package creation. Complete prebuilt assets skip Bun entirely, including when rebuilding a sdist. The helper lives under scripts, ships in the explicit-root sdist, and is not a runtime setting or runtime Bun dependency. A checksum-verified isolated Bun binary rebuilt clean source with no pre-existing static or node_modules directories; the corrected sdist contains neither workstation dependencies nor nested worktrees.

Example: install a verified wheel with uv tool install --python 3.13 <fork-wheel-url>. Replace its source explicitly using uv tool install --reinstall <new-artifact-url>; merely refreshing the historical URL still selects historical code. An isolated public-to-local-wheel source replacement with unchanged package metadata retained a synthetic dashboard setting and encryption key while runtime changed to 1.25.1. uvx and actual pip installs were separately checked; all used disposable data and tool/cache directories. Identity probes must run outside the checkout or with python -I, otherwise current-directory imports can shadow the installed app and falsely report its source version.

Source installs need the pinned Bun prerequisite and dependency network access, whereas complete wheel/sdist installs require only Python dependencies. Application data defaults to ~/.codex-lb regardless of tool/venv path, with CODEX_LB_DATA_DIR taking precedence; keep that data/key and the corresponding SQL backup across updates. Package smoke does not prove real account login, routing or older-schema compatibility. See [Python installation](../../../docs/deployment/python.md); macOS/Linux native package installs remain separate from the verified Windows run.

## Editable setup and frontend compilation

Windows diagnostic run 36904727598 on b89bd0a1 failed during uv sync, before Bun setup: the distribution hook also ran for Hatch's editable wheel version. Editable dependency setup now skips dashboard compilation only for that wheel version; standard wheel/sdist builds retain the exact Bun and complete-assets requirement. Existing development/CI workflows compile the frontend separately after installing Python dependencies. A fresh no-asset uv sync with incompatible host Bun verifies this boundary; a normal wheel build in the same environment must still fail. This also preserves backend-only CI setup without adding frontend dependencies to every job.

## Nix build-hook source membership

PR CI failed with missing scripts/hatch_build.py because explicit Nix source filesets selected metadata without its referenced plugin. Both packageSource and editableSource now include only scripts/hatch_build.py and scripts/build_dashboard.py. Complete standard Nix builds reuse the existing frontendAssets output; editable metadata loads the hook but leaves compilation explicit. This corrects a packaging compatibility seam without copying broad workstation state or changing Nix inputs/dependencies.

## Source checkout launchers

The source wrappers select their own checkout, use frozen uv dependencies, and prepare missing frontend assets before delegating to app.cli in the same interpreter. Help bypasses frontend preparation. PowerShell/batch preserve CLI failure status; batch pauses only for no-argument interactive use. Bash ships executable and execs uv, preserving foreground termination semantics. Paths with spaces and a foreign caller cwd were exercised on Windows PowerShell 5/pwsh/cmd and Ubuntu 24.04 WSL. A clean baseline was backend-ready but returned dashboard 503; the old PowerShell launcher returned zero on a CLI failure.

Linux startup revealed that bun run build can select host Node 18 via Vite shebang; build_dashboard now forces the pinned Bun runtime with --bun. The Linux audit used a checksum-verified isolated Bun 1.3.14 and forwarded SIGTERM: application shutdown completed, the listener disappeared, and uv returned expected signal code 143. Windows isolated Rust 1.96.0 native-helper build, discovery, protocol handshake and cleanup passed. These are source-install signals, not real account/OAuth/Codex traffic or macOS-native proof. Complete assets are reused; rebuild frontend explicitly after source changes. See the owning Python deployment page for prerequisite/setup/update commands.

## Nix flake workflow

The root flake is an additive installation and development path for Nix users.
It builds the same `codex-lb` distribution and CLI entry points as the Python
package while deriving dependency versions and hashes from `uv.lock`. The
flake inputs pin nixpkgs, uv2nix, pyproject.nix, and the shared build-system
overlay so a dependency update is an explicit lock-file change.

The package uses pyproject.nix's application wrapper rather than exposing its
internal Python virtual environment. Runtime dependencies are limited to the
project's default dependency set; metrics, tracing, documentation, and
development dependencies stay out of the proxy package. Nix builds the
dashboard from `frontend/bun.lock` and copies the compiled assets into the
Python wheel, matching the existing container and release build. Package source
filtering includes only the backend, frontend build inputs, configuration,
project metadata, license, and readme, so unrelated repository files do not
affect either source hash.

The development shell uses the default runtime dependencies plus the `dev`
dependency group. Documentation tooling and optional metrics and tracing
integrations stay out of the default shell so its closure remains focused. Its
project wheel is editable and points at the checkout through
`REPO_ROOT`; `UV_NO_SYNC=1`, `UV_PYTHON_DOWNLOADS=never`, and the pinned Python
3.13 interpreter keep uv from replacing the Nix-managed environment. Hatch's
editable path loads `editables` dynamically, so the flake supplies that helper
from the pinned build-system overlay as a dev-only build dependency. The
editable derivation hashes only project metadata, package roots, and the small
`config` package, so ordinary application source edits do not invalidate the
development shell.

Supported outputs are AArch64 Darwin, AArch64 Linux, and x86-64 Linux. The
pinned nixpkgs revision has dropped x86-64 Darwin support, so the flake does not
advertise an output that cannot evaluate. A missing compatible wheel or native
library after a lock update is expected to fail during `nix build` or
`nix flake check`, rather than falling back to an unpinned installer.

For example, from a checkout:

```bash
nix run .                 # start the proxy through app.cli:main
nix develop               # enter the editable development shell
nix build                 # build the wrapped codex-lb application
nix flake check           # build the default package
```

`nix run . -- --help` verifies the proxy command without starting the server.
The packaged app reads `.env` and `.env.local` from the directory where it is
launched: the wrapper defaults the `CODEX_LB_ENV_FILE` settings-load override
(an `os.pathsep`-separated path list) to the launch directory because the
packaged module root sits in the read-only Nix store where env files cannot
exist. An operator-provided `CODEX_LB_ENV_FILE` wins, and non-Nix launch
paths keep module-root discovery. Application state still follows the normal
data-directory rules and is never written into the immutable Nix store.

## Timeout Invariant Linter Scope

The timeout invariant linter is a startup `Settings` guardrail. Strict mode is
an opt-in startup or CI failure path for violating startup configuration, not a
general runtime timeout validator.

Validated inputs:

- The `Settings` object materialized at startup.
- Explicitly imported code constants used by the two constant-backed rules:
  model-registry refresh cadence and durable HTTP bridge retry-circuit TTL.

Known non-goals and follow-ups:

- Per-request `ContextVar` overrides are not revalidated. Current anchors:
  `app/core/clients/proxy.py:3450-3467`,
  `app/modules/proxy/_service/streaming/helpers.py:861-868`,
  `app/modules/proxy/_service/compact.py:727-738`,
  `app/modules/proxy/_service/transcribe.py:230-232`,
  `app/core/clients/files.py:77-90`, and
  `app/modules/proxy/service.py:1464-1478`.
- Runtime clamps and derived effective values are not fully modeled. Current
  anchors: `app/core/clients/proxy.py:1049-1088`,
  `app/core/auth/refresh.py:391-395`, and
  `app/modules/proxy/load_balancer.py:1846-1856`.
- Runtime DB, API-key, and model-source settings can affect timeout-bearing
  paths without startup revalidation. Current anchors:
  `app/core/config/settings_cache.py:22-36`,
  `app/modules/settings/api.py:547-710`,
  `app/modules/proxy/_service/streaming/retry.py:153-165`, and
  `app/modules/model_sources/forwarding.py:112-221`.

Example: `python -m app.core.timeout_invariants --strict` validates the
startup `Settings` view and exits nonzero when any enforced rule fails.
Running the same command without `--strict` reports violations but exits zero,
matching the default startup behavior.

`CODEX_LB_TIMEOUT_INVARIANT_VALIDATION_STRICT` is intentionally a setting
rather than a hard default because existing deployments may carry legacy timeout
values that deserve CRITICAL diagnostics first, not surprise startup refusal.
The default remains non-strict; operators and CI opt into fail-fast behavior.

## Helm termination-grace upgrade contract

The graceful-shutdown chart adds a render-time guard:
`terminationGracePeriodSeconds` must be at least
`config.shutdownDrainTimeoutSeconds + 32`. Existing values files, explicit
`--set` arguments, or values retained by `helm upgrade --reuse-values` below
that bound make `helm template`, `helm install`, and `helm upgrade` fail before
resources are applied. A failed upgrade leaves the existing release in place.

With the default 30-second drain timeout, the arithmetic minimum is 62 seconds
and the chart default is 65 seconds. An explicit retained value of 60 seconds,
the previous chart default, is therefore invalid. Before installing or
upgrading, raise every retained low value explicitly to at least the computed
minimum; setting 65 preserves the chart's default helper-launch headroom when
the drain timeout remains 30 seconds. Production overrides should retain
additional headroom for preStop helper launch.

For example, this retained value fails rendering:

```yaml
config:
  shutdownDrainTimeoutSeconds: 30
terminationGracePeriodSeconds: 60
```

When `--reuse-values` is used, removing
`terminationGracePeriodSeconds` from a new values file or omitting its `--set`
argument does not clear the stored 60-second value. That upgrade must set the
key explicitly to at least 62 seconds; setting it to 65 preserves the chart's
three seconds of helper-launch headroom. To adopt the 65-second chart default
without storing an override, use an intentional non-reuse or `--reset-values`
upgrade with `terminationGracePeriodSeconds` absent.

## Raw socket peer preservation and proxy projection

codex-lb captures the incoming ASGI client before delegating once to Uvicorn's
proxy projection. Shipped launchers disable the outer server middleware so raw
transport policy can use the original peer while downstream handlers still see
the projected client and scheme. The `forwarded_allow_ips` setting (env
`FORWARDED_ALLOW_IPS`, alias `CODEX_LB_FORWARDED_ALLOW_IPS`, also loadable from
`.env` files) is the sole trust input and keeps Uvicorn's semantics unchanged.

For example, a TCP peer at `10.0.0.8` may project client `192.168.65.1` and
scheme `https`; raw-peer authorization still evaluates `10.0.0.8`.

## NEXT-RELEASE QUEUE (do not lose)

Work queued for the release after the one that shipped the
settings-surface reduction (issue #1340, phases 1-4 + retention dashboard
settings, merged as PRs #1351, #1360, #1362, #1363, #1364 in v1.21.x):

1. **Drop the deprecated prewarm request-log columns (phase B).**
   `prewarm_canary_bucket` and `prewarm_eligible_reason` have been unwritten
   since phase 4 and are no longer mapped by the `RequestLog` ORM model since
   `retire-prewarm-canary-column-mappings` (v1.25); the physical columns are
   allow-listed in `_LEGACY_EXTRA_COLUMNS` (`app/db/migrate.py`). They could
   not be dropped in the same release that retired the mapping: the Helm
   migration Job runs before old replicas drain, and a previous-release
   replica renders explicit NULLs for every mapped column in its request-log
   INSERTs, so dropping the columns while v1.24 still mapped them would have
   failed its inserts and full-entity reads during the roll. Once v1.25 is the
   oldest supported release, add the Alembic drop revision (batch-mode
   `drop_column` for SQLite, nullable re-add on downgrade) and remove the two
   allow-list entries in the same PR.
2. ~~**Retire the retention env aliases.**~~ Done in
   `remove-dead-env-settings` (first release after v1.24.0): the env fields are gone and
   `CODEX_LB_REQUEST_LOG_RETENTION_DAYS` /
   `CODEX_LB_USAGE_HISTORY_RETENTION_DAYS` are in `_REMOVED_SETTINGS` for
   their warning release. See `openspec/specs/data-retention/context.md`.
3. **Retire the removal warning itself.** `_REMOVED_SETTINGS` and
   `warn_removed_settings()` in `app/core/config/settings.py` are a
   one-release courtesy per removed batch ("at least one release"). The
   phase 1-4 names were pruned by `remove-dead-env-settings` (their warning release shipped in
   v1.22-v1.24); the six names removed by that change, together with
   `CODEX_LB_UPSTREAM_STREAM_TRANSPORT` (`remove-upstream-stream-transport-env`),
   are pruned in the release after the one that ships them. Drop the mechanism
   only once no batch is pending.

## Settings-surface reduction rationale (issue #1340, phases 1-4)

PRINCIPLES.md P2: "a setting the operator never needs to touch is a
default in disguise." The `Settings` class carried 165 env-settable fields
before phase 1; phases 1-4 removed 52 of them (plus adding `CODEX_LB_TRACE`).
Selection rule for every phase: removal is provably zero-risk вЂ” each
removed field keeps its exact previous default as the new fixed value, so
behavior is byte-identical for any install that never overrode it, and the
only behavioral seam (the removed-settings warning) is additive.

Capability choice: `deployment-installation` owns the operator env-var
contract at settings-load time (see the data-directory resolution
requirement), so the fixed-constants + removal-warning requirement lives
here rather than in `contribution-simplicity`, which governs the
contribution/review process, not runtime behavior.

### Removed fields by phase

Phase 1 (24 removed, 1 added; zero-risk internals):

- OAuth protocol identity (6): `CODEX_LB_AUTH_BASE_URL`
  (`https://auth.openai.com`), `CODEX_LB_OAUTH_CLIENT_ID`
  (`app_EMoamEEZ73f0CkXaXp7hrann`), `CODEX_LB_OAUTH_ORIGINATOR`
  (`codex_chatgpt_desktop`), `CODEX_LB_OAUTH_SCOPE`
  (`openid profile email`), `CODEX_LB_OAUTH_REDIRECT_URI`
  (`http://localhost:1455/auth/callback`), `CODEX_LB_OAUTH_CALLBACK_PORT`
  (1455) вЂ” module constants in `app/core/config/settings.py`; changing any
  of them breaks login.
- Auth guardian tuning (7 fields removed): interval 21600, max refresh
  age 43200, batch size 100, concurrency 3, jitter 300.0, failure backoff
  base 300.0 / max 3600.0. The separate max-age constant was later retired;
  candidate selection now reuses the fixed eight-day
  `TOKEN_REFRESH_INTERVAL_DAYS` policy in `app/core/auth/refresh.py`. The
  remaining guardian constants live in `app/core/auth/guardian.py`, and the
  single switch is the dashboard setting `auth_guardian_enabled`
  (`CODEX_LB_AUTH_GUARDIAN_ENABLED` is a deprecated fallback while the
  dashboard value is unset).
- Debug log booleans (6): the `CODEX_LB_LOG_PROXY_*` /
  `CODEX_LB_LOG_UPSTREAM_*` booleans became `CODEX_LB_TRACE` channels
  (`shape`, `shape_raw_cache_key`, `payload`, `service_tier`,
  `upstream_summary`, `upstream_payload`); empty default = all off. This
  is an incident-debugging knob for interactive use only; there is no
  correct steady-state value other than "off".
- Bulkhead per-class overrides (3): http/websocket/compact limits always
  derive from `CODEX_LB_BULKHEAD_PROXY_LIMIT` (http = websocket = proxy
  limit; compact = min(http, 16), 0 when http is 0).
- Token-refresh claim polling (2): wait 8.0 s, poll 0.25 s вЂ” constants in
  `app/modules/accounts/auth_manager.py`.
  `CODEX_LB_TOKEN_REFRESH_CLAIM_TTL_SECONDS` stayed in this phase because
  its floor validation referenced settings that were still configurable;
  `constantize-core-tunables` later fixed those operands too, so the TTL
  is now the code helper `max(30 s, admission wait + 2 x refresh timeout)`
  in `app/modules/accounts/auth_manager.py` (same 30 s result) and the
  env name is removed.

Phase 2 (15 removed):

- Scheduler cadences (4): quota planner tick 300 s (the old
  `max(60, ...)` clamp became moot and was dropped), automations poll
  30 s, model-registry refresh 300 s, sticky-session cleanup 300 s вЂ”
  constants next to their scheduler builders; every `*_ENABLED` switch
  remains.
- Codex client fingerprint (3): OS `Mac OS 26.5.0`, arch `arm64`,
  terminal `iTerm.app/3.6.10` вЂ” `_FINGERPRINT_*` constants in
  `app/core/clients/proxy.py`, maintained in lockstep with
  `CODEX_LB_MODEL_REGISTRY_CLIENT_VERSION` bumps (which stays a setting:
  it doubles as the degraded-startup catalog floor).
- Live-usage write coalescing (2): min interval 5.0 s, queue size 512 вЂ”
  constants in `app/modules/usage/live_ingest.py`.
- Request-log count-cache TTL (1): fixed 30.0 s in
  `app/modules/request_logs/repository.py` (the test suite patches the
  constant to 0 where exact totals matter).
- Circuit-breaker tuning (2): failure threshold 5, recovery timeout 60 s
  вЂ” constants in `app/core/resilience/circuit_breaker.py`. The Helm chart
  values `config.circuitBreakerFailureThreshold`,
  `config.circuitBreakerRecoveryTimeoutSeconds`, and
  `config.stickySessionCleanupIntervalSeconds` were removed in the same
  change so a default install does not trip its own removal warning.
- Memory warning threshold (1): derived as 80% of
  `CODEX_LB_MEMORY_REJECT_THRESHOLD_MB` in
  `app/core/resilience/memory_monitor.py`. The warning has no meaning on
  its own вЂ” it exists to announce that the reject threshold is being
  approached. The only lost configuration is a warning-only setup with no
  reject threshold, an observability half-measure the log stream covers
  anyway. `CODEX_LB_MEMORY_REJECT_THRESHOLD_MB` stays: it is the one
  genuine deployment decision (it depends on host memory size), default 0
  = fully off.
- Images internals (2): `resolve_default_host_model()` in
  `app/core/openai/host_models.py` selects `gpt-5.6-luna`, then `gpt-5.5`,
  using registry plan visibility and suppression. If neither qualifies,
  it falls back to `gpt-5.6-luna`. Images and default account probes share
  this resolver. The internal host model is never echoed to Images clients.
  The partial-images cap is fixed to 3 in
  `app/core/openai/images.py` (an upstream streaming contract).
  `CODEX_LB_IMAGES_DEFAULT_MODEL` stayed in this phase as the public API
  contract for clients that omit `model`; `constantize-core-tunables`
  later fixed it as `DEFAULT_PUBLIC_IMAGE_MODEL = "gpt-image-2"` in
  `app/core/openai/images.py` (nobody ever pointed it elsewhere, and the
  public default is a contract precisely because it does not move per
  deployment).

Phase 3 (10 removed):

- DB pool tuning (4): background pool size / max overflow always derive
  from `database_pool_size` / `database_max_overflow` (nothing ever set
  the overrides; unconditional derivation also collapses the `background`
  branch out of the engine-kwargs helper so pre-ping/recycle regressions
  like #672 cannot diverge between the two engines); pool checkout
  timeout fixed 30.0 s and recycle window fixed 1800 s
  (`_POSTGRES_POOL_*` constants in `app/db/session.py`).
  `CODEX_LB_DATABASE_POOL_SIZE` / `CODEX_LB_DATABASE_MAX_OVERFLOW` stay:
  PostgreSQL HA operators must budget both independently pooled engines in
  every supported one-worker replica:
  `(pool_size + max_overflow) x 2 x replicas`, while reserving server
  connections for PostgreSQL internals, migrations, and operations. The owned
  CLI launcher pins one worker; custom multi-worker launchers are unsupported.
  The Helm chart pins both pool inputs.
- Soft-drain/probe thresholds (6): drain at 85%/90%, error window 60 s /
  count 2, probe quiet 60 s, success streak 3. They encode the
  deterministic-failover design and interlock вЂ” raising one without the
  others degrades failover in non-obvious ways вЂ” and
  `app/core/balancer/logic.py` already declared identical constants as
  `evaluate_health_tier` parameter defaults, so the settings were a second
  source of truth for numbers that must not drift. The function keeps its
  full parameter surface for tests; production call sites rely on the
  constant defaults. `CODEX_LB_SOFT_DRAIN_ENABLED` and
  `CODEX_LB_DETERMINISTIC_FAILOVER_ENABLED` stay as the subsystem
  switches.

Phase 4 (3 removed; prewarm canary scaffolding):

- `CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_CODEX_PREWARM_CANARY_PERCENT`
  and the `..._ALLOW_API_KEY_IDS` / `..._DENY_API_KEY_IDS` cohort lists
  (plus their validator). The canary machinery was one-time rollout
  instrumentation for a finished experiment, not an operator contract.
  Production was verified live on 2026-07-15 before removal: every
  replica ran `prewarm_enabled=False`, percent unset (`None`), empty
  allow/deny lists вЂ” and the `canary_percent=None` code path (treat all
  eligible requests, `legacy_all`) is exactly the new unconditional
  behavior, so nothing changed for defaults or production.
  `..._PREWARM_ENABLED` stays (default off, mid-rollout): enabling it is
  a real operator decision; only the scoping machinery went away.
  `prewarm_status=canary_miss` is unreachable and removed from the
  observability contract; see
  `openspec/specs/proxy-runtime-observability/context.md`.
  If a future feature needs percentage or cohort-scoped rollout, that is
  a new OpenSpec change with its own design вЂ” re-introducing these
  settings verbatim is explicitly not the path.

## Deprecation policy for removed settings

`extra="ignore"` on `Settings` makes removed env vars inert the moment the
fields are deleted; the startup WARN (`warn_removed_settings()` in
`app/core/config/settings.py`, called from the `app/main.py` lifespan) is
one release of courtesy so operators notice stale configuration. The
warning lists names only, never values. `_REMOVED_SETTINGS` holds only the
most recent removal batch: once a batch's warning release has shipped its
names are pruned (they stay inert), so the list never accumulates.

### Removed by `remove-dead-env-settings` (first release after v1.24.0)

Six env fields whose documented behavior was already dead or deprecated:

- `CODEX_LB_REQUEST_LOG_RETENTION_DAYS`, `CODEX_LB_USAGE_HISTORY_RETENTION_DAYS`
  вЂ” deprecated aliases for the dashboard retention settings since
  v1.21.x; NULL dashboard values are now disabled (`data-retention`).
- `CODEX_LB_HTTP_DOWNSTREAM_TRANSPORT_POLICY`,
  `CODEX_LB_OPENAI_CACHE_AFFINITY_MAX_AGE_SECONDS`, `CODEX_LB_WARMUP_MODEL`
  вЂ” only ever copied into the `dashboard_settings` row when it was first
  created, so on every initialized deployment the env value was ignored
  while docs and the Helm chart (`config.cacheAffinityMaxAgeSeconds`,
  removed) presented it as live configuration. The first-created row now
  takes the column defaults (`smart`, `1800`, `gpt-5.4-mini`), which equal
  the former env defaults.
- `CODEX_LB_HTTP_RESPONSES_SESSION_BRIDGE_GATEWAY_SAFE_MODE` вЂ” zero
  readers; only the dashboard column was ever consulted.

`CODEX_LB_WORKERS_PER_INSTANCE` was also dropped as a `Settings` field but
is NOT a removed setting: it is a startup guard (only `1` is supported) and
keeps rejecting any other value with the same error
(`proxy-admission-control`).

### Removed by `constantize-core-tunables` (first release after v1.25.0-beta.5)

Twenty-seven never-tuned core tunables from the `MIGRATING` backlog became
fixed constants at their previous defaults (slop-removal 0908, K1; the
triage evidence is per field: definition line unchanged since introduction,
no Helm/.env.example/docs/issue/incident mention, never set in production).
Behaviour is unchanged; each env name gets the one-release WARN.

- Upstream transport: `CODEX_LB_MAX_SSE_EVENT_BYTES` (16 MiB),
  `CODEX_LB_UPSTREAM_RESPONSE_CREATE_MAX_BYTES` (15 MiB, derived from the
  frame budget), `CODEX_LB_UPSTREAM_COMPACT_TIMEOUT_SECONDS` (no constant вЂ”
  the dashboard `compact_request_budget_seconds` was already the only total
  cap that ever applied).
- Auth / token refresh: `CODEX_LB_OAUTH_TIMEOUT_SECONDS` (30 s),
  `CODEX_LB_TOKEN_REFRESH_TIMEOUT_SECONDS` (8 s),
  `CODEX_LB_TOKEN_REFRESH_CLAIM_TTL_SECONDS` (helper, 30 s),
  `CODEX_LB_PROXY_REFRESH_FAILURE_COOLDOWN_SECONDS` (5 s),
  `CODEX_LB_PROXY_ADMISSION_WAIT_TIMEOUT_SECONDS` (10 s, single home in
  `app/modules/proxy/work_admission.py`).
- Usage polling: `CODEX_LB_USAGE_FETCH_TIMEOUT_SECONDS` (10 s),
  `CODEX_LB_USAGE_FETCH_MAX_RETRIES` (2), `CODEX_LB_USAGE_REFRESH_ENABLED`
  (always on, including the request-path refreshes),
  `CODEX_LB_USAGE_REFRESH_INTERVAL_SECONDS` (60 s; the 180 s freshness
  horizon is derived in `app/core/usage/refresh_policy.py`),
  `CODEX_LB_USAGE_REFRESH_AUTH_FAILURE_COOLDOWN_SECONDS` (300 s),
  `CODEX_LB_LIVE_USAGE_INGESTION_ENABLED` (always on),
  `CODEX_LB_RATE_LIMIT_RESET_CREDITS_REFRESH_INTERVAL_SECONDS` (60 s).
  `CODEX_LB_RATE_LIMIT_RESET_CREDITS_REFRESH_ENABLED` is NOT in this batch:
  it migrated to the dashboard setting
  `rate_limit_reset_credits_refresh_enabled`
  (`dashboard-managed-background-jobs`), where it joins
  `auth_guardian_enabled` and `automations_scheduler_enabled` under
  Settings в†’ Advanced в†’ Background jobs.
- Scheduler toggles: `CODEX_LB_STICKY_SESSION_CLEANUP_ENABLED`,
  `CODEX_LB_MODEL_REGISTRY_ENABLED` (always on),
  `CODEX_LB_QUOTA_PLANNER_SCHEDULER_ENABLED` (folded into the dashboard
  `quota_planner_settings.mode = "off"`, which already stopped every tick;
  no new column).
- Ingress / images / models: `CODEX_LB_MAX_DECOMPRESSED_BODY_BYTES` (32 MiB)
  and `CODEX_LB_MAX_DECOMPRESSED_RESPONSES_BODY_BYTES` (128 MiB) in
  `app/core/ingress_limits.py`, the same constant that seeds `--ws-max-size`;
  `CODEX_LB_IMAGE_INLINE_FETCH_ENABLED` (always on) and
  `CODEX_LB_IMAGE_INLINE_ALLOWED_HOSTS` (the allowlist was never populated;
  the scheme, literal-host and disallowed-IP SSRF guards stay);
  `CODEX_LB_IMAGES_DEFAULT_MODEL` (`gpt-image-2`);
  `CODEX_LB_OPENAI_PROMPT_CACHE_KEY_DERIVATION_ENABLED` (always on; Helm
  `config.promptCacheKeyDerivationEnabled` removed).
- Process admission gates: `CODEX_LB_PROXY_TOKEN_REFRESH_LIMIT` (64),
  `CODEX_LB_PROXY_UPSTREAM_WEBSOCKET_CONNECT_LIMIT` (128),
  `CODEX_LB_PROXY_COMPACT_RESPONSE_CREATE_LIMIT` (64); every gate always
  exists. `CODEX_LB_PROXY_RESPONSE_CREATE_LIMIT` (256) stays configurable.

Helm also drops `config.stickySessionCleanupEnabled` so a default install
does not trip its own removal warning. `CODEX_LB_TOKEN_REFRESH_INTERVAL_DAYS`
was in the triage batch but was deferred one change: it had a live consumer,
and `constantize-token-refresh-interval` finished it (below).

### Removed by `constantize-token-refresh-interval`

`CODEX_LB_TOKEN_REFRESH_INTERVAL_DAYS` is the 28th and last field of the
`MIGRATING` backlog. The proactive refresh window is now the fixed eight-day
`TOKEN_REFRESH_INTERVAL_DAYS` in `app/core/auth/refresh.py`, its previous
default. It was never a recovery lever: an account is refreshed on demand on
any upstream 401 whatever the window says, so shortening it only adds
exchanges and lengthening it only defers one.

`constantize-core-tunables` kept the field because the traffic-parity canary
was the one live consumer вЂ” it pinned the variable to `365` so a controlled
run could not exchange its isolated, single-use refresh token against the real
authorization host (`AUTH_BASE_URL` is a protocol constant, so redirecting
`CODEX_LB_UPSTREAM_BASE_URL` at the local fixture does not cover OAuth). That
pin is replaced by a repository-owned preflight in
`scripts/traffic_analysis/fast_canary_suite.py`: the suite stamps the isolated
`auth.json`'s recorded refresh time вЂ” every key the account importer accepts
for it (`lastRefreshAt`, `last_refresh`), so no stale alias outranks the stamp
вЂ” to the current instant before either runner starts, so the imported account
is inside the fixed window for the whole run.
The stamp is strictly stronger than the pin, which only ever reached the
failure-matrix subprocess while the raw HTTP/2 runner relied on a host-local
`CODEX_LB_TOKEN_REFRESH_INTERVAL_DAYS=365` line of its own; both host-local
lines can now be deleted, and until they are, they only produce the removed
setting WARN.

With this removal the `MIGRATING` backlog in `app/core/config/tiers.py` is
empty: every T3 field has a `dashboard_settings` column of the same name or a
`DASHBOARD_HOMES` mapping. An empty registry is the intended terminal state,
not a lint error.

## Example

An operator running `CODEX_LB_LOG_UPSTREAM_REQUEST_PAYLOAD=true` upgrades:
startup logs

```
removed setting(s) ignored: CODEX_LB_LOG_UPSTREAM_REQUEST_PAYLOAD вЂ” values are now fixed; see PRINCIPLES.md P2 / issue #1340
```

and the equivalent incident-debugging behavior is re-enabled interactively
with `CODEX_LB_TRACE=upstream_payload`. Startup never fails because of a
removed setting, and the fixed built-in value is used.

## Fork Helm and Nix installation verification (2026-10-02)

The fork chart uses `frozen811/codex-lb`; public aliases remain historical. Source
installs build and explicitly select the audited image. Bundled PostgreSQL is
pinned to the verified public 18.6 digest in values.yaml. The chart dependency
lock pins chart 18.6.7, independently of the database image digest.

Fresh external installs with chart-created app credentials run a regular
migration Job alongside Secrets and schema-gated pods. A post-install hook
would deadlock with Helm `--wait`. Existing DB credentials alone do not imply
the encryption-key Secret exists; only an existing app Secret permits the
pre-install hook. Upgrades retain pre-upgrade hooks and drain requirements.

Runtime metadata and diagnostic/conversation scratch state use the mounted
`/tmp/codex-lb`; DB rows and the shared key stay durable in PostgreSQL/Secret.
Scratch files are ephemeral. Archive retention needs an operator-supplied mount
and the existing conversation archive setting. Helm rollback never restores
a compatible DB by itself; back up DB and key together.

Nix uses Bun's copyfile backend because an unprivileged Linux build user may
not hardlink immutable store files. Nix files use LF so embedded build-phase
shell fragments also run from Windows/WSL checkouts. For example, `nix build .`
followed by the result executable in a different launch directory keeps
`.env` / `.env.local` discovery local to that directory; explicit env-file and
process env overrides retain precedence. x86_64 Linux package/dev-shell builds
and startup are verified; ARM64/Darwin, real OAuth and Codex generation remain
separate runtime checks. See docs/deployment/nix.md and issues-check.md section 22.

## Configuration and paired restore rehearsal (2026-10-02)

Purpose: remove working-directory and storage ambiguity from SETUP-02/03. Python
dotenv discovery remains module-root anchored to avoid reading an unrelated
project's settings. For example, an installed package launched from a project
directory uses explicit `CODEX_LB_ENV_FILE=/absolute/project/.env.local` when that
file is intended. Ordered file paths use the platform separator; process values
win. Compose injects its server env_file as process values, while Nix supplies
launch-directory paths through its wrapper. Listener CLI defaults are separate.
Missing files/unknown names remain ignored for compatibility; recognized invalid
values fail validation. Negative CLI keep-alive now fails before startup.

SQLite snapshots use the backup API, include committed WAL data and are restored
into an empty directory with the matching key. PostgreSQL/MySQL require separate
logical dumps. An external key/archive/spool path is not included just because
the application volume is copied. Zero-config remains the base single-instance
path; this does not add a setting, dependency or schema revision. Directory
ownership and readable key material are prerequisites for non-root containers.

Fresh CLI SQLite processes and disposable PostgreSQL/MySQL Docker databases
verified dashboard overrides across restarts and matching-key decryptability
after restore. A dashboard override of 9 stayed effective while the environment
changed from 4 to 6/7; clearing it restored 7. Source-mounted Python runtime used
the existing image only for its dependency environment. New Unix keys were 0600
under UID 1000; unwritable storage refused startup. Windows force-termination is
crash-style cleanup; Linux Docker SIGTERM completed graceful shutdown. A wrong
key refused SQLite startup. Physical upstream credentials were never used.

Rollback means restoring the old binary's paired pre-upgrade snapshot. An older
binary pointed at a newer schema is not a verified downgrade. Platform/runtime
limits and exact checks live in issues-check.md section 24 and the archived
repair-setup-configuration-data-network verification report; operator commands
are rendered in docs/configuration.md and docs/database.md.

## Explicit-source update and paired rollback (SETUP-08, 2026-10-02)

Purpose: separate source selection, running image identity and storage recovery.
Local remote names are not repository authority: this checkout's origin is
Soju06 while fork is Frozen811. The update guide uses explicit fork URL/fullSHA,
clean-tree and failure checks. A disposable checkout with upstream origin
successfully fetched and detached at fork f52adb7274c96c0702e19aa02eabd4f1c7556231;
the shared checkout and its uncommitted fixes were not switched.

The historical public Linux/amd64 runtime manifest
31557c9d04de1fb263b022b0ab1309c4d020675309a69ecac2d19365d35b3087
reports1.25.0-beta.9. A local copy-source overlay over the audited dependency
image reports1.25.1. In isolated SQLite storage, old startup/seed, current
migration/recreate and old-image restore of its paired pre-upgrade snapshot
preserved settings, paused-account ciphertext/decryptability and key. Both
current and restored schema checks passed. The old binary never opened the
newly migrated original store; rollback used an empty separate restore volume.

For example, retarget a mutable test tag while its old container is running:
the tag's image ID changes, the container's ID/version do not. Recreating it
selects the new image. Local image IDs, registry manifest/index digests,
package metadata, runtime version and source SHA are distinct evidence. This
does not certify every upgrade/downgrade pair or publish new artifacts.

Failure guidance now covers package versus source asset recovery, selected
venv/interpreter, optional native transport and DB/upstream stages. The runtime
missing-assets503 hint uses pinned/frozen Bun with forced Bun execution rather
than a host Node shebang, and advises complete-artifact reinstall for packages.
See docs/deployment/docker.md, docs/deployment/python.md and issues-check§26.

## Optional startup-probe timing

The [startup timing contract](spec.md#requirement-helm-startup-probe-timing-is-configurable) allows legitimate slow cold starts without changing the application's handler or other probes. The default budget remains 5 seconds of initial delay plus 30 failures at a 2-second period, with Kubernetes' effective 1-second timeout and success threshold one.

For example, Helm values `startupProbe: {failureThreshold: 90}` increase that failure budget while readiness and liveness remain unchanged. Null, fractional, boolean, nonpositive timing values and invalid success thresholds fail schema validation. External-DB and staging rendering require their documented database source separately; startup tuning does not supply credentials. See the [chart guide](../../../deploy/helm/codex-lb/README.md#startup-probe-timing).
