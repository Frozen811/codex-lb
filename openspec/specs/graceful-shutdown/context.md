# Graceful shutdown context

Requirements are in [spec.md](spec.md). The owned CLI commits one drain
deadline before closing connections and finalizes admitted work/settlement
within that process deadline plus its cleanup reserve.

## Ring registration and heartbeat DB cleanup

The ring task owns SQLAlchemy sessions while registering the instance and
refreshing its heartbeat. Immediate Task.cancel at shutdown can interrupt
SQLite NullPool's asynchronous connection reset/close. A constrained Linux
startup/SIGTERM reproduction identified `_register_and_heartbeat` as the
connection owner; a held-registration regression reproduces the failure
deterministically.

The lifespan now signals a local stop event. Idle heartbeat intervals and
registration retry waits wake on that event, while the current DB operation
finishes within the existing bounded background-task grace. Membership is
marked stale after stopping this owned task, so a late normal registration
cannot immediately overwrite the stale marker. No new timeout setting is
introduced. Wedged work still uses the existing cancellation fallback and
undrained-task clean-marker guard; the process deadline remains authoritative.

Example: SIGTERM during a ring insert held for another 0.5s lets that insert and
connection close complete, stops subsequent heartbeat work and then ages the
membership row. An idle task does not wait through its full heartbeat interval
or five-second registration backoff. Tests retain pool-error, stale-row,
leader-release and bounded-exit assertions.

## Direct-local lifecycle controls (SETUP-09, 2026-10-02)

Purpose: keep preStop/operator control independent of forwarded user identity.
Start, stop and status now require captured raw loopback peer, projected
loopback client and no nonempty forwarded client-IP hints. Missing capture
fails closed. Raw loopback alone would allow a remote user of a local proxy;
projected loopback alone would allow a spoofing remote socket. Direct local
calls remain valid even when global proxy/firewall trust settings are enabled.

For example, execute preStop inside the app's container namespace against
127.0.0.1. A request through nginx with forwarded client evidence receives403
instead of changing or revealing drain state. Headerless direct drain is
reversible; a deadline-bearing preStop/signal commits the existing one-way
barrier. Readiness becomes503 while /health/live remains200 until process exit.

## Verification and platform boundaries

New route tests reproduced six unauthorized200 outcomes before the fix; final
route/unit tests also verify missing capture, conflicting forwarded evidence,
local reversal and existing deadline/cancellation behavior. Source Docker
runtime reports the actual middleware drain envelope separately from the raw
health handler's exception message. Existing queued/task/finalization tests
remain unchanged in their assertions and timing budgets.

Five WebSocket process and two database-shutdown tests require POSIX signal
delivery. Windows skips them explicitly; all seven executed on Linux/amd64
with frozen test dependencies. Fixture startup now uses a bounded30s monotonic
window for cold imports; drain/forced-exit deadlines were not increased. Native
Windows TerminateProcess/Ctrl+C and Linux SIGTERM/SIGINT are not equivalent.
See issues-check.md section26 for runtime identities, exact outcomes and limits.

## Persistence ownership and interrupted stops (2026-10-09)

The [ownership requirements](spec.md) distinguish handler completion from detached persistence completion. A done settlement remains observable while its callback can still create a reservation-release fallback. Status uses validated counts and flags: pending owners report `pending`, completed ownership reports `drained`, and unavailable or inconsistent observation reports `unknown` without a count. This is an instantaneous view, not a historical write-success certificate.

For example, after an HTTP stream ends, `in_flight=0` and `request_persistence_pending=1` can coexist. Only after settlement callbacks release ownership does the count become zero. Fallback-cancelled scheduler cleanup stays in the clean-shutdown proof even when the stop caller is interrupted. Cooperative grace still leaves its worker running when the caller is cancelled.

Drain denial for `/codex/responses` and its slash variant retains the same retryable HTTP 503, Retry-After 5 and OpenAI envelope as v1/backend-api proxy paths. Other WebSocket protocols retain their generic detail response. Windows in-process and SQLite tests do not substitute for POSIX process-signal or external database evidence.
