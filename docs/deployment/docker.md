# Docker

## Build the fork locally

Use a Docker Engine with BuildKit and Linux containers. From a checkout of
[`Frozen811/codex-lb`](https://github.com/Frozen811/codex-lb), build the selected source revision:

```bash
git clone https://github.com/Frozen811/codex-lb.git
cd codex-lb
docker build -t codex-lb:local .
```

Then follow the Basic run command below. This
builds the checkout you selected, including its dashboard and native helper;
it does not pull a public release image. Local installation has been checked
with Linux/amd64 containers on Docker Desktop for Windows. Other CPU
architectures and real-account routing require separate validation.

The image runs without root and stores data in `/var/lib/codex-lb`. Prefer a
named volume: an arbitrary host bind mount needs permissions matching the
container user. Check startup without displaying account credentials:

```bash
docker inspect codex-lb --format '{{.State.Health.Status}}'
docker exec codex-lb python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:2455/health/ready').status)"
```

To update a local build, select the desired source revision, rebuild the
image, stop and remove only the `codex-lb` container, then repeat the run
command with the same named volume. Back up the volume before updating;
keeping a volume does not guarantee that an older image can read a newer
database schema.

## Update identity and rollback

Stop application writers and retain a [paired DB/key backup](../database.md#backup-restore-and-rollback),
configuration and the old executable/image identity before updating. Select a
reviewed **fork** source or artifact explicitly; a local remote named `origin`
can be upstream. Complete frontend assets are reused by source launchers, so
rebuild changed frontend sources before restarting a checkout installation.

For Docker, compare the candidate image and the running container separately:

```bash
docker image inspect codex-lb:local --format '{{.Id}}'
docker inspect codex-lb --format '{{.Image}}'
docker exec codex-lb python -c "import app; print(app.__version__)"
```

The first two values are local image IDs, not registry manifest/index digests.
A running container keeps its image ID when a tag is retargeted or pulled;
`docker restart` runs that same container/image. Recreate it with the explicitly
selected candidate to change code. A mutable `latest` tag can be cached or
retargeted, while a full `repository@sha256:...` selects a registry artifact.
Fetching new source does not update a public-image installation. The server-only
source Compose file uses `pull_policy: build`; follow its source build commands
instead of expecting `docker compose pull` to select newer source.

After recreation, check runtime version and selected image/source identity,
`/health/ready`, dashboard HTML plus referenced assets, saved settings and
account inventory. Verify credential decryptability without printing tokens;
real upstream operation needs its own authenticated test. Readiness and a
version string alone do not prove the intended update.

Rollback uses the old pinned executable/image **and its compatible pre-upgrade
DB/key snapshot**. Restore into an empty isolated store first, check schema and
application data, then choose the cutover deliberately. Retaining a volume does
not make it safe to run old code on a migrated schema. `helm rollback` and image
retagging do not restore database contents. Migration-specific downgrade notes
describe only that revision, not every release you might cross.

An isolated Linux/amd64 rehearsal on 2026-10-02 replaced the historical pinned
runtime `1.25.0-beta.9` with a local source overlay reporting `1.25.1`, retained
settings/account ciphertext/key, recreated the candidate, then restored the old
snapshot with the old image. Both schema and product data checks passed. The
candidate reused an audited dependency image and copied current local source;
this does not certify a new public release or every downgrade pair. Detailed
artifact/source evidence remains in the repository's issues-check registry.

## Public fork image

The public `latest` and `1.25.1` aliases were checked on 2026-10-01: both
resolve to historical source `f622c5632013d24ce9236d176113087b387c7990`, not
the current checkout fixes. The runtime reports `1.25.0-beta.9` despite the
OCI version label `1.25.1`. This image has a Linux/amd64 runtime manifest;
the additional `unknown/unknown` entry is an attestation, not ARM64 support.
Use the source build above for the selected checkout. An existing public
release is a separate installation channel, and a new source pull does not
update it.

To reproduce that historical image without a GitHub login:

```bash
docker pull ghcr.io/frozen811/codex-lb@sha256:ad9aa84b12bce9f6afc63adb3aa86e73f6aafca1814e6f20b486b00f21c60447
```

Use that full image reference in place of `codex-lb:local` in Basic run.
The historical image's named-volume startup, readiness, assets and recreation
were tested on Linux/amd64. It has no built-in Docker HEALTHCHECK; use the
Python readiness probe below (the health-status inspect applies to local
builds). Real OAuth/login and account routing were not part of that smoke.
Changing tags or digests requires deliberate selection of a tested release;
back up data first and recreate only your application container with its
existing volume. Do not assume an older image can open a migrated schema.

## Basic run

After building `codex-lb:local` above, run **one** of these alternatives.
Docker must use Linux containers. An existing container named `codex-lb`
must be updated deliberately as described above before reusing its name.

Linux/WSL/macOS Bash:

```bash
docker volume create codex-lb-data
docker network inspect codex-lb-net >/dev/null 2>&1 || docker network create codex-lb-net
docker run -d --name codex-lb \
  --network codex-lb-net \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local
```

Windows PowerShell (backticks must be the final character on each continued line):

```powershell
docker volume create codex-lb-data
docker network inspect codex-lb-net *> $null
if ($LASTEXITCODE -ne 0) { docker network create codex-lb-net }
docker run -d --name codex-lb `
  --network codex-lb-net `
  -p 2455:2455 -p 1455:1455 `
  -v codex-lb-data:/var/lib/codex-lb `
  codex-lb:local
```

Ports:

- `2455` — dashboard + proxy API
- `1455` — OAuth login callback (needed while adding accounts)

The volume retains the default SQLite database, encryption key and archives under
`/var/lib/codex-lb/` across container recreation. External PostgreSQL/MySQL and
independently configured key/archive/spool paths need separate backups. Follow
the [paired backup and restore guide](../database.md#backup-restore-and-rollback)
before updating; avoid removing the volume when recreating the container.

## Switching Wi-Fi or other networks

When a laptop switches from one Wi-Fi network to another—for example, from home Wi-Fi to a phone hotspot—or when a VPN connects or disconnects, existing internet connections may briefly break. Docker can also keep using a DNS server from the previous network. DNS is the service that finds the network address for names such as `chatgpt.com`; if Docker's copy is out of date, codex-lb may report timeouts while contacting OpenAI even though the host browser works.

codex-lb retries only when the transport can prove that the request failed before it was sent. Merely seeing no output is not enough: if a request may already have reached OpenAI, codex-lb returns the network error without resending it, which avoids accidentally starting the same response twice. In either case, it avoids treating a laptop-wide DNS problem as a problem with an individual account. It cannot, however, repair a Docker DNS service that remains pointed at the old network.

For laptops that switch networks frequently:

Bare `uvx codex-lb` installs the upstream PyPI package. For the
fork, use the source-build instructions above or a verified fork release
artifact; a PyPI command without a fork source does not select this checkout.

- **Host Python on Linux, macOS, and Windows:** select the explicit fork source or historical wheel in the [Python guide](python.md). Running on the host avoids Docker's additional DNS layer.
- **Docker Engine on Linux (verified with `systemd-resolved`):** use host networking so the container shares the host resolver path. This survives network switches only when the host exposes a stable resolver address, such as the `127.0.0.53` `systemd-resolved` stub. If the host's `/etc/resolv.conf` points directly to a DNS server supplied by Wi-Fi or other DHCP, that address can still become stale. In that case, configure a stable host resolver, follow the [bridge-listener runbook](https://github.com/Frozen811/codex-lb/blob/main/openspec/specs/deployment-networking/context.md#diagnostics-and-recovery), or prefer `uvx`. Use the following command instead of the portable Docker command above.
- **Docker Desktop on macOS or Windows:** Docker Desktop 4.34 and later offers opt-in host networking, but containers still run through Docker Desktop's virtual machine and its DNS behavior can vary by version and configuration. This setup has not been verified as a reliable fix for switching networks. Keep Docker Desktop current; if failures persist, prefer the native `uvx` installation.

```bash
docker volume create codex-lb-data
docker run -d --name codex-lb \
  --network host \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local
```

In the verified Docker Engine setup on Linux, host networking does not use `-p`; codex-lb still listens on ports 2455 and 1455. It also removes Docker's network-namespace isolation. The command is an opt-in path to a stable host resolver, not a DNS fix by itself.

## Docker Compose

The root `docker-compose.yml` is the **development** setup. It builds a backend
and a Vite frontend; it is not a server-only production install. Docker Compose
2.24.0 or later is needed for its optional `.env.local` support, as described
in the [Compose env-file reference](https://docs.docker.com/reference/compose-file/services/#required).
From the fork checkout, without creating an env file:

```bash
docker compose up -d --build server frontend
docker compose ps
```

Open `http://localhost:5173` for the development dashboard. The backend is at
`http://localhost:2455`, and account login callbacks use port `1455`. The
frontend proxies API and health requests to the backend service. Check the
proxy with `http://localhost:5173/health/ready`.

Both application services run without root; the frontend owns its source and
dependency cache directories as the `bun` user.

For source changes, run `docker compose watch server frontend` in another
terminal. Backend source sync restarts its service; frontend sync leaves the
Vite process running. Dependencies and local frontend env files are excluded
from sync. Rebuild after changes to dependency lockfiles.

Stop with `docker compose down`; the data volume is retained. Do not add
`--volumes` when you want to keep accounts and settings. The supplied files
use fixed volume names, so `-p` alone does not create an independent data
store for a second installation. They are single-replica setups.

For a server-only source install with optional external PostgreSQL via env, use
[`docker-compose.prod.yml`](https://github.com/Frozen811/codex-lb/blob/main/docker-compose.prod.yml) — it defines
only the `server` service. Its `pull_policy: build` always builds the checkout
as `codex-lb:local`, including when an older image is cached, following the
[Compose pull-policy contract](https://docs.docker.com/reference/compose-file/services/#pull_policy).
It uses volume-backed SQLite without an env file. The optional `postgres` / `postgres-upgrade` / `mysql` profiles live in the root
[`docker-compose.yml`](https://github.com/Frozen811/codex-lb/blob/main/docker-compose.yml) (see [Database](../database.md)):

```bash
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml ps
```

For external PostgreSQL, create `.env.local` before startup with your existing
database URL (percent-encode special characters in user/password):

```dotenv
CODEX_LB_DATABASE_URL=postgresql+asyncpg://user:password@db.example.internal:5432/codexlb
```

The database must already exist and be reachable from the application
container. `localhost` refers to that container; use a reachable database DNS
name, or `host.docker.internal` for a host database on Docker Desktop. Allow
the container's connections in the database firewall/access policy. Configure
TLS for your server as shown below. Startup applies migrations and readiness requires database
access. Check `http://localhost:2455/health/ready`, the dashboard and logs.

For PostgreSQL with certificate and hostname verification, add these driver
variables to `.env.local` and obtain the CA certificate from your database
operator. Both the runtime driver and migration driver use these values:

```dotenv
PGSSLMODE=verify-full
PGSSLROOTCERT=/run/db-trust/ca.crt
```

Create `compose.db-tls.yml` with a read-only mount of that public CA file:

```yaml
services:
  server:
    volumes:
      - ./db-ca.crt:/run/db-trust/ca.crt:ro
```

```bash
docker compose -f docker-compose.prod.yml -f compose.db-tls.yml up -d
```

The URL hostname must match the database certificate. This uses standard
[PostgreSQL driver variables](https://www.postgresql.org/docs/current/libpq-envars.html),
without adding an application setting or conflicting driver-specific URL
query parameters. A controlled PostgreSQL TLS installation with migrations,
runtime SQL and readiness has been verified; the actual remote DNS, firewall
and certificate chain still depend on your database deployment. Keep the TLS
override in subsequent update/recreate commands if you use it.

After changing `.env.local`, recreate the application with the same volume:

```bash
docker compose -f docker-compose.prod.yml up -d --force-recreate server
```

This Compose file builds source; `docker compose pull` does not update it.
For an update, select the desired checkout revision and repeat `up -d` (build
caches are reused). Keep the application volume, which contains its encryption
key even with external PostgreSQL, and back up the external database separately.
Restoring the external database without the matching key cannot restore account
access. Do not run two applications against the same SQLite volume.

For PostgreSQL and MySQL profiles and the Postgres 16 → 18 upgrade runbook, see [Database](../database.md).

## Distroless local build

```bash
docker build -f Dockerfile.distroless -t codex-lb:distroless-local .
```

Use `codex-lb:distroless-local` in the Basic run command with a separate
container name and named volume if you keep another install running. Both
images use the same ports and persistent data path. Stop the existing
container before reusing its ports or SQLite volume.

The distroless image has no shell. Use `docker logs codex-lb` for diagnostics
and the Python readiness command above rather than `docker exec ... sh`.
Its named-volume startup, readiness, assets and data retention have been
checked on Linux/amd64. Local build support does not imply that a distroless
tag is published in the fork registry.

## Persistent debug logs

`docker logs` output lives in the container's own log file and is deleted when
the container is recreated. To keep logs across redeploys, write them to the
data volume with the server's log flags. In Compose, extend the server
`command:`:

```yaml
    command:
      - python
      - -m
      - app.cli
      - --host
      - 0.0.0.0
      - --port
      - "2455"
      - --log-level
      - info
      - --log-file
      - /var/lib/codex-lb/logs/codex-lb.log
```

Use `debug` only while diagnosing; it raises codex-lb's own loggers, never uvicorn's. The file rotates at 50 MiB with 10 backups, as one rotation sequence. Docker's own json-file log is separate and unrotated by default; bound it with `logging: {driver: json-file, options: {max-size: "50m", max-file: "5"}}` on the service. With the default named volume it is
on the host under the volume's mountpoint
(`docker volume inspect codex-lb-data --format '{{.Mountpoint}}'`). Keep it
private: see [Server log flags](../reference/settings.md#server-log-flags-not-settings)
for what is and is not redacted.

## Auth mode examples

**Authelia / trusted header**

```bash
docker run -d --name codex-lb \
  -p 2455:2455 -p 1455:1455 \
  -e CODEX_LB_DASHBOARD_AUTH_MODE=trusted_header \
  -e CODEX_LB_DASHBOARD_AUTH_PROXY_HEADER=Remote-User \
  -e CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS=true \
  -e CODEX_LB_FIREWALL_TRUSTED_PROXY_CIDRS=172.18.0.0/16 \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local
```

**Hard override / no app-level dashboard auth**

```bash
docker run -d --name codex-lb \
  -p 2455:2455 -p 1455:1455 \
  -e CODEX_LB_DASHBOARD_AUTH_MODE=disabled \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local
```

For Helm, pass the same values through `extraEnv`. What these modes mean and when to use them is covered in [Authentication](../authentication.md).

---

*Specs: [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation) · [deployment-networking](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-networking) · [proxy-runtime-observability](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/proxy-runtime-observability)*
