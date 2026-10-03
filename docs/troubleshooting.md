# Troubleshooting

## Startup, readiness and failure stages

Check the selected executable/image and effective configuration before changing
timeouts. `docker restart` preserves the old container/image; source/pinned-image
selection and recreation are explained in the [update guide](deployment/docker.md#update-identity-and-rollback).

| Signal / stage | What it proves | Recovery / next check |
|---|---|---|
| Process exits before an HTTP listener | Startup failed; no readiness claim is possible | Read the named validation/migration/prerequisite error in private logs and correct that input |
| `/health/startup` 200 | Application startup completed | Continue with readiness and intended product paths |
| `/health/live` 200 | HTTP process can answer liveness | Does not prove DB, assets, accounts or upstream access |
| `/health/ready` 200 | Infrastructure DB/bridge readiness | Fetch dashboard/assets and make an authenticated client request separately |
| Ready 503 after drain, live 200 | Intentional admission drain | Wait for active work/shutdown; don't treat it as an upstream-account outage |
| Docker `healthy` | The configured Docker health command passed | Identify the actual command/image; historical images may have no HEALTHCHECK |

Readiness deliberately excludes upstream degradation, dashboard assets and
the optional native helper so an upstream outage does not permanently evict an
otherwise ready replica. During drain, the middleware can return
`{"error":{"type":"service_unavailable","message":"Server is draining"}}`
before the readiness handler; its HTTP status is 503. A ready process is not a
complete installation or a successfully authenticated account.

| Failure | Observable diagnosis | Recovery |
|---|---|---|
| Invalid recognized env value | Validation names the field, e.g. `leader_election_enabled`; exit is nonzero | Correct its type/value and restart with the intended env-file selection; unknown names can be ignored |
| Database unavailable at startup | Migration/connect failure, nonzero exit | Verify DB host/port/credentials and network namespace, then retry; container localhost is the app itself |
| Dashboard assets absent | Ready can be 200 while `/` returns 503 with a build/reinstall hint | For a checkout use pinned Bun, frozen dependencies and `bun --bun run build`; reinstall/rebuild a complete package/image for that channel |
| Optional native helper absent | PATH discovery returns no helper; normal infrastructure startup can still pass | Verify the selected interpreter/dependencies; Python transport remains available for its supported routes. Install/build the correct helper when the intended contract requires it |
| HTTP port occupied | CLI bind failure and nonzero exit | Stop the owning test/service deliberately or choose another HTTP/published port; callback1455 is separate |
| Upstream unavailable after readiness | Authenticated generation fails at connect/stream; ready can remain 200 | Check that destination's DNS/TCP/TLS/proxy path and safe error code/request ID. Don't drop mandatory auth or certificate checks |

Use the executable from the selected venv/tool. Calling the system Python while
excluding the venv dependencies from PATH can produce a module-import error
unrelated to helper availability. Keep DB/key snapshots and real request data
private; diagnostic evidence normally needs stage, status/code, request ID,
selected version/image and a redacted exception type, not credentials.

At WARNING or higher, a log message's unquoted `Authorization` field is masked
through the end of its line, including any trailing `status` or `code` text.
Complete quoted values retain the surrounding field context. Put diagnostic
status/code in structured log fields or on the next line to keep them visible.
See the owning [proxy-runtime-observability spec](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/proxy-runtime-observability).

### Internal drain and process shutdown

Internal `/internal/drain/start`, `/stop` and `/status` are direct loopback
operator/preStop controls. They require captured local socket provenance and
reject forwarded caller hints, including a forged loopback address. Run them
inside the selected container/process namespace; don't expose them through the
dashboard proxy. A headerless local operator drain remains reversible, while a
deadline-bearing preStop/signal commits shutdown and cannot be reopened.

Use the foreground owned CLI/launcher and your supervisor's normal termination
path. Linux SIGTERM first closes new admission, allows existing work within the
shared drain deadline, then finalizes tasks/DB/helper cleanup before exit.
Check terminal completion or bounded timeout, shutdown-complete logs, exit/OOM
state and absence of a listener. Forced kill cannot prove graceful cleanup.
Windows `TerminateProcess` and POSIX signals differ: Linux-container/WSL signal
tests do not certify native Windows console-close/Ctrl+C behavior. Keep the
supervisor's stop budget longer than the configured drain plus cleanup reserve;
see the [shutdown contract](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/graceful-shutdown).

The [platform evidence matrix](deployment/python.md#platform-and-topology-evidence)
separates executed tests from declared targets. These failure/diagnostic
contracts belong to [user-documentation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/user-documentation)
and [deployment-installation](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/deployment-installation).

## Usage and quota

**Why does codex-lb still say `rate_limited` when Codex Desktop says the window reset?**
codex-lb refreshes usage on its own schedule and treats upstream samples conservatively. The full policy — refresh cadence, expiry, and why displays can briefly disagree with upstream — is documented in the
[usage refresh policy context](https://github.com/Frozen811/codex-lb/blob/main/openspec/specs/usage-refresh-policy/context.md).

## Streaming

**Codex CLI falls back to POST instead of WebSockets.**
Run the [WebSocket verification steps](client-setup.md#verify-websocket-transport). If codex-lb sits behind a reverse proxy, make sure it forwards WebSocket upgrades — see [Remote Access](deployment/remote.md).

## Fast Mode, Ultrafast, and service tiers

Fast Mode, Ultrafast, and service-tier behavior is documented in the
[Responses API compatibility context](https://github.com/Frozen811/codex-lb/blob/main/openspec/specs/responses-api-compat/context.md#fast-mode-and-service-tiers).

## Old Codex sessions missing after migrating

`codex resume` filters by `model_provider` — re-tag old sessions with the built-in retag command. See
[session retagging](client-setup.md#migrating-from-direct-openai-session-retagging).

## Locked out of the dashboard

**The company login is down, or the authenticator for the only administrator is gone.**
Four host commands act on the database directly to re-open local sign-in, reset a password, or turn a sign-in provider off — see
[Company Sign-In and Recovery](sso.md#host-recovery-commands).

## After upgrading, old pods fail every settings read

**Symptom.** The migration succeeded and the new pods are healthy, but pods still running the
previous release answer `500` on anything that loads dashboard settings — sign-in included. The
migration log carries one warning naming `20260912_010000_drop_legacy_dashboard_credentials`.

That release drops three `dashboard_settings` columns that every earlier build still maps, and those
builds load the settings row whole. The database is correct and complete: the same upgrade copied the
dashboard credentials onto the account rows before it dropped the columns they came from, so **do not
re-run or downgrade the migration**. Finish the roll instead — stop the old replicas (scale to zero,
or stop the old colour of a blue/green pair) and let the new ones serve. The upgrade refuses nothing
and needs no second command; the stop is the part that has to happen first, which is why the
[Kubernetes upgrade sequence](deployment/kubernetes.md#upgrading-to-the-release-that-drops-the-legacy-dashboard-credential-columns)
puts it before the migration Job.

---

*Spec: [usage-refresh-policy](https://github.com/Frozen811/codex-lb/tree/main/openspec/specs/usage-refresh-policy)*
