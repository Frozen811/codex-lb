# Remote Access

Running codex-lb on a server and connecting from other machines involves three pieces: the one-time dashboard bootstrap token, API keys for clients, and (usually) a reverse proxy.

## First login

Setting the initial dashboard password remotely requires a one-time bootstrap token printed to the server logs — see [Getting Started](../getting-started.md#remote-setup-bootstrap-token).

## Client access

Remote clients hit the protected proxy routes, which reject non-local requests until proxy authentication is configured. Enable [API key auth](../api-keys.md) and give each client a key from the dashboard.

## Listeners and client endpoints

`--host` is a bind address. `127.0.0.1` limits a host process to that machine; `0.0.0.0` listens on all IPv4 interfaces, but is not a client destination. Choose a reachable server IP/DNS name and the **published** HTTP port for clients. Binding IPv4 does not imply an IPv6 listener.

| Process / caller | HTTP or database destination |
|---|---|
| Native app and browser on the same host | `http://127.0.0.1:2455`; a host DB can use `127.0.0.1:5432` / `:3306` |
| Browser on LAN / another host | `http://server-ip-or-dns:published-port`; bind/admit that interface and retain remote authentication |
| App container and DB container on one user-defined bridge | `postgres:5432` / `mysql:3306`; container loopback points at the app itself |
| App container to DB on Docker Desktop host | `host.docker.internal:host-db-port`; the DB listener/firewall must admit this path |
| App container to DB on native Linux Docker host | Add `--add-host=host.docker.internal:host-gateway` and use a DB listener reachable on that gateway; a host loopback-only DB is not reachable this way |
| Host client to published container | `http://127.0.0.1:host-port` locally, or `http://server-ip:host-port` remotely; for `8080:2455`, use 8080 |
| WSL process / Windows client | Determine the WSL networking mode and reachable host first. Localhost forwarding, mirrored networking and NAT differ; verify from the actual client. WSL loopback is not a general LAN address |

Publishing `127.0.0.1:8080:2455` limits the host port to local clients. An unrestricted `8080:2455` mapping may expose it on the host's interfaces. Docker Desktop's host endpoint is not automatically available on native Linux. In Linux host-network mode, loopback belongs to the host and `-p` is not used; see [Docker networking](docker.md#switching-wi-fi-or-other-networks) for resolver and isolation limits.

Port **2455** is the HTTP listener (dashboard, API, SSE and WebSocket). Port **1455** is the OAuth callback listener, started only during an account login and tied to the fixed `http://localhost:1455/auth/callback` redirect. `PORT` / `--port` changes HTTP only. Publishing 1455 does not start the callback listener; a separate Codex login already using it can prevent binding. For a remote browser, a loopback SSH tunnel such as `ssh -N -L 1455:127.0.0.1:1455 user@server` forwards the browser's callback to the selected instance; leave dashboard/API access and TLS configured separately. Container deployments must publish the callback to the server-side loopback endpoint used by the tunnel.

| Check | Meaning / next step |
|---|---|
| `curl --fail http://server:port/health/ready` from the intended client | Inbound HTTP and readiness; also fetch dashboard/assets. It does not test outbound upstream access |
| Address-in-use at CLI startup / Docker port allocation | Another listener or container owns the selected HTTP/callback port. Choose an unused HTTP host port; stop or separately arrange the conflicting callback listener |
| Name-resolution failure inside app container | Test DNS in that namespace; host browser success does not prove container resolution |
| DNS succeeds, connect times out / refused | Check upstream/DB destination port, listener, route and egress firewall |
| TLS handshake/certificate failure | Check certificate trust and outbound proxy configuration in the application environment; do not disable verification to conceal it |

For a container, run the checks from that container, for example:

```bash
docker exec codex-lb python -c 'import socket; print(socket.getaddrinfo("chatgpt.com", 443))'
docker exec codex-lb python -c 'import urllib.request; r=urllib.request.urlopen("https://auth.openai.com", timeout=10); print(r.status)'
```

A 401/403 HTTP response proves DNS/TCP/TLS reached an HTTP endpoint, not OAuth success; an HTTP proxy can also answer before the origin. A successful response without account credentials is only a transport probe. Test actual authenticated upstream behavior separately. Container DNS forwarding can become stale when switching host networks; the [Docker guide](docker.md#switching-wi-fi-or-other-networks) documents the recovery boundaries.

## Reverse proxy

For nginx on the same host as codex-lb, copy the
[nginx example](https://github.com/Frozen811/codex-lb/blob/main/deploy/nginx.conf)
to `/etc/nginx/conf.d/codex-lb.conf`, inside the nginx `http` context. It
listens on port 8080 and proxies to loopback port 2455. Start the selected fork
package with explicit proxy trust, then validate and reload your nginx:

```bash
export CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS=true
export CODEX_LB_FIREWALL_TRUSTED_PROXY_CIDRS=127.0.0.1/32
codex-lb --host 127.0.0.1 --port 2455
# In another terminal, after installing the example:
sudo nginx -t
sudo nginx -s reload
curl --fail http://127.0.0.1:8080/health/ready
```

Use the executable from your verified [Python](python.md) or [Nix](nix.md)
installation. The sample overwrites incoming forwarded headers with the
direct client address, preserves Host including port, and forwards HTTP/1.1
WebSocket upgrades with SSE buffering disabled. It is a local HTTP example;
configure a TLS listener and certificates before using dashboard credentials
across an untrusted network. A successful readiness check does not prove
OAuth, real Codex requests or certificate trust.

For containers, `127.0.0.1:2455` means the proxy container itself. Use the
backend's service name on the shared network or deliberately share its network
namespace, and trust only the proxy's actual source address/CIDR. Forwarded
client identity is needed even for a loopback proxy so remote users are not
mistaken for local clients. Keep the backend port private.

### TLS and the two forwarding trust settings

For TLS termination, replace the sample's `listen 8080;` with a TLS listener and
your certificate/key paths in the same `server` block, retaining all proxy
headers, streaming and timeout directives:

```nginx
listen 8443 ssl;
ssl_certificate /etc/nginx/tls/fullchain.pem;
ssl_certificate_key /etc/nginx/tls/privkey.pem;
```

Use a certificate for the actual client DNS name. With a public certificate,
clients use their normal trust store; for a private CA, install that CA or pass
it explicitly when checking readiness:

```bash
curl --fail --cacert /path/to/your-ca.pem https://lb.example.com:8443/health/ready
```

Keep certificate verification enabled. Opening the TLS endpoint does not verify
OAuth or account entitlement. The proxy sample limits HTTP request bodies to
32 MiB; increase that nginx limit deliberately if your client requires larger
payloads and verify it against the application's own request budget.

Two settings control different decisions:

- `FORWARDED_ALLOW_IPS` (alias `CODEX_LB_FORWARDED_ALLOW_IPS`) controls whether
  the socket peer may project `X-Forwarded-For` and `X-Forwarded-Proto` into the
  client address and request scheme. Its default trusts `127.0.0.1` only.
- `CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS=true` together with
  `CODEX_LB_FIREWALL_TRUSTED_PROXY_CIDRS` authorizes application client identity
  and dashboard `trusted_header` evidence from that proxy's captured socket IP.

The same-host example works with the loopback projection default. For a proxy
container on another address, configure **both** trust sets for that proxy's
actual source IP/network. Keep them narrow and overwrite client-supplied
forwarding/identity headers at the proxy. Trusting scheme projection alone
does not authorize a dashboard identity. The proxy's socket IP can legitimately
differ from the forwarded user's IP; that user's IP remains relevant to
firewall/locality checks.

Verify one authenticated request from the intended client through each path.
For SSE, observe the first event before completion to detect buffering; a
successful final response alone can hide buffering. WebSocket needs a 101
upgrade and an application event exchange. A synthetic echo test proves proxy
transport only. HTTP keep-alive, upstream read/send timeouts, application stream
idle budgets and WebSocket idle cleanup are separate limits; test reconnects
against the transport your client actually selected. codex-lb returns failures
after uncertain dispatch rather than promising transparent replay.

OAuth login listens separately on port 1455 while adding an account. If the
browser runs on another machine, forward that callback port securely to the
same application instance; the nginx dashboard listener does not forward it.
No `codex-lb.service` unit or one-command remote installer is shipped here.
For an independently configured supervisor, keep its selected executable,
environment and persistent DB/key paths together when updating.

When codex-lb sits behind a reverse proxy (nginx, Traefik, Caddy, Authelia, ...):

- **Forward WebSocket upgrades.** Codex streaming uses WebSockets on `/backend-api/codex/responses`; a proxy that only forwards plain HTTP silently degrades to POST fallback. See [verify WebSocket transport](../client-setup.md#verify-websocket-transport).
- **Declare the proxy as trusted** so codex-lb sees real client IPs from `X-Forwarded-For`:

```bash
export CODEX_LB_FIREWALL_TRUST_PROXY_HEADERS=true
export CODEX_LB_FIREWALL_TRUSTED_PROXY_CIDRS=172.18.0.0/16
```

Only sources inside the trusted CIDRs may set forwarded headers; everything else is treated as the direct peer address.

- **Optionally delegate dashboard auth** to the proxy with `trusted_header` mode — see [Authentication](../authentication.md), and [Company Sign-In and Recovery](../sso.md) for the local sign-in policy and the host recovery commands.
- **Preserve the browser's `Host` header (with port).** For state-changing dashboard requests over plain `http://`, codex-lb compares the browser's `Origin` with the request scheme + `Host` and answers `403 cross_site_request_rejected` on a mismatch. Use nginx `proxy_set_header Host $http_host;` or Apache `ProxyPreserveHost On` (Traefik and Caddy pass `Host` by default) — see [Cross-site request protection](../authentication.md#cross-site-request-protection).
- **Leave the idle keep-alive window alone unless a client needs more.** codex-lb closes idle client connections after 300 s (`--timeout-keep-alive` / `UVICORN_TIMEOUT_KEEP_ALIVE`, process environment only). The value must exceed the largest connection-pool idle timeout of your proxy and clients by a safety margin that absorbs the network round-trip and timer scheduling (practically `S >= 2C`; reqwest default: 90 s, so 300 s leaves 3.3x; Codex CLI itself opens a fresh connection per `/responses` request) so a pooled connection is never reused as the server closes it; raising it into hours only holds idle sockets longer. If a reverse proxy fronts codex-lb, keep the proxy's *upstream* idle/pool timeout below `--timeout-keep-alive`, or raise `UVICORN_TIMEOUT_KEEP_ALIVE` above it. The race window is one RTT wide at the server's timeout and does not depend on request body size, so large compaction POSTs need no extra allowance.

---

*Specs: [deployment-networking](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-networking) · [api-firewall](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/api-firewall) · [http-ingress-limits](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/http-ingress-limits) · [admin-auth](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/admin-auth)*
