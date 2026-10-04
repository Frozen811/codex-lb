# Local refusal provenance audit

Scope: UP-ISSUE-2388. Upstream issue bodies for 2388, 2389 and 2033 were read through the GitHub API on 2026-10-04. Graph lookup/traces selected the producers and their current source was inspected. The scan includes transport-coded constructors, envelope producers and two eventless gates. Locations below use symbols and branch descriptions so formatting changes do not invalidate the verdict.

| Producer / branch | Verdict and evidence |
|---|---|
| helpers: parallel fork incompatible anchored session | Mark local. Only called during get-or-create, before submission; existing model-fork choice preserved. Route fault injection executes the real compatibility predicate and raise. |
| helpers: incompatible admission handoff | Mark local. Admission recovery refuses creation before returning a session; it does not dispatch the new request. Public-route fault injection invokes the real admission recovery method. |
| helpers: recovery lease renewal fail-closed | Mark local. Renewal is reached by get-or-create before submission. Real recovered model-transition child + failing durable renewal refuses turn N+1 without sending it. |
| mixin: owner-instance metadata lookup failure | Mark local. Get-or-create ring lookup precedes creation/submission. Actual getter with unavailable owner metadata, route and SQLite reservations covered. |
| mixin: active ring lookup failure | Mark local. Same pre-dispatch boundary, separate producer. Actual getter with unavailable membership covered. |
| session registry: recovery claim missing durable tables | Mark local. Recovery creation cannot publish its durable identity; no response.create has been submitted. Actual model-transition child plus claim OperationalError covered. |
| submit: circuit suppression | Mark local only for a request with zero send attempts, no response ID/events and no previous replay. Above operation registration, enqueue and send. Canonical, slash, native backend and signed internal routes before commitment, plus committed native delivery. Raw-HTTP replay permission remains a separate, stricter proof. |
| submit: retiring session | Same request proof. Above enqueue/send, after the already-observed-response guard. |
| submit: closed and unregistered hard session | Same request proof. Refuses before reconnect or enqueue. |
| submit: closed after reconnect returned false | Same request proof. Reconnect used send_request=False; exception from reconnect itself remains transport provenance. |
| submit: closed/replaced after admission | Same request proof. Lifecycle fence precedes queue publication and send. |
| submit: stale-anchor generation claim missed | Same request proof. Generation CAS refusal precedes queue publication and send. Actual refusal producer, injected CAS miss; real submission cleanup and reservations covered. |
| submit lease helper: session closed during lease acquisition | Same request proof. Detached acquired lease is released before refusal; caller has not dispatched. Actual acquire interleaving covered. |
| stream startup: continuity cooldown | Mark local only with the same no-send/no-response/no-replay proof. Before submit; releases reservation. Its established public code is bridge_eventless_timeout, outside the issue's original four-code set. |
| mixin: initial continuity-lost branches (three) | Already local. They refuse owner/anchor resolution before creation. Existing regressions retained. |
| mixin: alias continuity-lost branch | Already local. Getter refuses before a session returns. Existing regression selection retained. |
| streaming: durable owner lookup unavailable | Already local. Before creation/submission. |
| submit: conclusively denied proxy-injected anchor | Already local. Before enqueue/send; existing denial and signed-forwarding tests retained. |
| helpers: excluded bound account | Leave unmarked. Shared by creation and reconnect; reconnect may follow an attempted send. No request proof is available in this producer. |
| mixin: old reader did not shut down | Leave unmarked. Reconnect may be recovery of already-dispatched work; not a provable pre-dispatch refusal on every path. |
| submit: request already has response events | Leave unmarked. Explicit evidence of prior upstream dispatch. |
| prewarm failure | Leave unmarked. A warmup frame was enqueued and sent upstream; authored failure is not a local admission refusal. |
| shutdown error for inflight futures | Leave unmarked. The inflight map also owns reconnect handoff futures for existing sessions, so this shared error has no per-request dispatch proof. |
| stream cooldown refreshed after submit | Leave unmarked. Request already submitted and detached before error propagation; delivery is ambiguous. |
| stream propagation of upstream failed event | Leave unmarked. Carries authored upstream terminal/error provenance after dispatch. |

There are 14 newly marked producer branches, six already-marked branches and seven retained mixed/post-dispatch contexts (27 candidate contexts). These counts include the startup/post-submit eventless gates and envelope adapters. Pure forwarding adapters preserve owner-supplied provenance; they cannot infer it from status/code. Other error codes (404 continuity signals, 413 payload admission, operator drain and capacity errors) are outside the four-code audit.

The new route tests retain real loopback WebSockets, real SQLite reservations and cleanup. Compatibility/admission callbacks and specific metadata/CAS/database interleavings are fault-injected; they are not live-provider or multi-process race certification. Five separate negative controls refuse to attach local provenance after a send attempt, response ID, response event or replay marker.
