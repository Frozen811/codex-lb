# Graceful shutdown context

Requirements are in [spec.md](spec.md). The owned CLI commits one drain
deadline before closing connections and finalizes admitted work/settlement
within that process deadline plus its cleanup reserve.

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
