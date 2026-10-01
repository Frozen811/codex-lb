# Getting Started

codex-lb runs with zero configuration — every setting has a working default, and Docker vs. host paths are auto-detected.

## Quick Start

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

# or Nix
nix run github:Soju06/codex-lb
```

Open [localhost:2455](http://localhost:2455) → Add account → Done.

Choose the installation channel deliberately: [Docker](deployment/docker.md)
builds the selected fork checkout; [Python packages](deployment/python.md)
explains historical wheel identity and current source prerequisites. Bare
`uvx codex-lb` selects upstream PyPI, and the Nix example above is also upstream.

Next: point your coding agent at codex-lb — see [Client Setup](client-setup.md).

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

**Local access** (localhost) bypasses bootstrap entirely — no token needed.

Running behind a reverse proxy or exposing codex-lb to other machines? See [Remote Access](deployment/remote.md) and [Authentication](authentication.md).

---

*Spec: [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation)*
