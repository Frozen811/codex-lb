# Getting Started

codex-lb runs with zero configuration — every setting has a working default, and Docker vs. host paths are auto-detected.

## Quick Start

The multi-line command below uses **Bash** (Linux/WSL/macOS), from a selected
fork checkout with Docker running. Windows readers should use the
[PowerShell Docker example](deployment/docker.md#basic-run) or
[Python / checkout launchers](deployment/python.md#run-from-a-fork-checkout).
The Docker, wheel and Nix commands are alternatives; choose one.

```bash
# Docker (from a Frozen811/codex-lb checkout; see the Docker guide)
docker build -t codex-lb:local .
docker network inspect codex-lb-net >/dev/null 2>&1 || docker network create codex-lb-net
docker run -d --name codex-lb \
  --network codex-lb-net \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local

# or the historical fork wheel (see the Python guide before choosing)
uvx --from https://github.com/Frozen811/codex-lb/releases/download/v1.25.0-hardened.3/codex_lb-1.25.1-py3-none-any.whl codex-lb

# or Nix from a Frozen811/codex-lb checkout (see the Nix guide)
nix run .
```

Open [localhost:2455](http://localhost:2455) → Add account → Done.

Choose the installation channel deliberately: [Docker](deployment/docker.md)
builds the selected fork checkout; [Python packages](deployment/python.md)
explains historical wheel identity and current source prerequisites. Bare
`uvx codex-lb` selects upstream PyPI. The [Nix guide](deployment/nix.md)
explains fork source pins, writable storage and tested platform boundaries.

Next: point your coding agent at codex-lb — see [Client Setup](client-setup.md).

Check [platform/topology evidence](deployment/python.md#platform-and-topology-evidence)
for the executed OS/architecture combinations, and the [update/rollback checks](deployment/docker.md#update-identity-and-rollback)
before replacing an existing installation. Startup/readiness and product-path
failures have separate [diagnostics](troubleshooting.md#startup-readiness-and-failure-stages).

## Remote setup (bootstrap token)

When accessing the dashboard remotely for the first time, a bootstrap token is required to set the initial password.

**Auto-generated (default):** On first startup (no password configured), the server generates a one-time token and prints it to logs:

```bash
docker logs codex-lb
# ============================================
#   Dashboard bootstrap token (first-run):
#   <token>
# ============================================
```

Open the dashboard → enter the token + new password → done. The token is shared across replicas and remains valid until a password is set. In multi-replica setups, replicas must share the same encryption key (the Helm chart default) for restart recovery to work — see [Kubernetes deployment](deployment/kubernetes.md).

**Manual token:** To use a fixed token instead, set the env var before starting:

```bash
docker run -d --name codex-lb \
  -e CODEX_LB_DASHBOARD_BOOTSTRAP_TOKEN=your-secret-token \
  -p 2455:2455 -p 1455:1455 \
  -v codex-lb-data:/var/lib/codex-lb \
  codex-lb:local
```

**Direct local access** bypasses the initial bootstrap token check when the
application verifies the request as local. A browser using `localhost` through
Docker, a VM or a reverse proxy can appear non-local to the service, so the URL
alone is not proof of locality. Forwarded remote clients still need bootstrap;
after password setup, dashboard sign-in remains required. Client API keys are
separate from the bootstrap token and dashboard password.

Running behind a reverse proxy or exposing codex-lb to other machines? See [Remote Access](deployment/remote.md) and [Authentication](authentication.md).

## Adding an account from another machine

The browser OAuth redirect uses `http://localhost:1455/auth/callback` on the
browser's machine. The callback listener belongs to the selected codex-lb
instance, separate from its HTTP port. A remote browser can use a secure SSH
forward to that instance, or paste the resulting callback URL into the
dashboard's manual-callback input. The callback URL contains temporary login
credentials: use that input directly, not a public issue or shared log.

If port 1455 is occupied, codex-lb records `OAuth callback listener unavailable`
with the bind host/port and exception type, releases failed listener resources,
and keeps the browser flow pending for manual completion. Check the owning
process before arranging the callback route. Device-code login is a separate
choice in the dialog, not proof that a published callback port is listening.
An imported auth file is another separate path and must come from the intended
account. Verify the account identity/status after login/import; don't treat
readiness as proof of successful authentication.

For an existing Business/Enterprise personal access token, select **Add account →
Import → Access token**. Paste the token into the masked field, enter its email
and upstream account ID, choose the plan and optionally specify the workspace
ID. The dashboard shows the imported account as non-refreshable: import a new
token after expiry or rejection. Auth-file imports remain available for other
credential exports. Replacing an existing slot requires **Import without
overwrite** to be disabled; otherwise a separate credential slot can be created.
The [account-import spec](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/account-import)
owns this contract; the operator supplies metadata and local import does not
verify upstream entitlement.

These paths are governed by [OAuth callback privacy](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/oauth-callback-privacy)
and [dashboard authentication](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/admin-auth).

---

*Spec: [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation)*
