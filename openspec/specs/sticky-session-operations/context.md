# Sticky Session Operations Context

## Purpose and Scope

This capability covers operational control and routing semantics for sticky-session mappings. It distinguishes hard account/session ownership from bounded cache locality, including bare process-session spillover under account caps.

See `openspec/specs/sticky-session-operations/spec.md` for normative requirements.

## Decisions

- Sticky-session rows store an explicit `kind` so prompt-cache cleanup can target only bounded mappings.
- Bare process-session headers use a header-inaccessible, source-separated storage key and are soft only for self-contained pre-visible work.
- Account-cap spillover is request-local: it selects an alternate without deleting or rebinding the process-session row. The same rule covers a soft TTL-bounded `prompt_cache` owner that is absent from a request's candidates only because it is capped or because that request's own retry loop excluded it after a transient failure while its persisted status is still recoverable; an isolated, explicitly reallocated, paused/deactivated or out-of-scope owner is still rebound.
- Raw and legacy Codex rows remain hard during rolling upgrades because they may represent explicit turn-state ownership.
- A raw legacy Codex owner can be abandoned only for an explicit goal-continuation restart whose canonical upstream payload passes the account-neutral fresh-replay proof, and only while that owner has a persisted unavailable status. Canonicalization keeps accepted compatibility fields and transport envelopes from changing classification. The compare-and-set marker is scoped to `session_header`, so an explicit turn-state lookup with colliding raw text retains the stored owner; a concurrent rebind or owner recovery still wins. The scoped marker deliberately leaves the historical global-tombstone timestamp empty, so replicas that do not understand scope continue to fail closed on the retained owner. Current Codex also sends `thread-id`; that locality source does not block the process-session exception. The raw compatibility lookup stays a `session_header` interpretation so a scoped tombstone cannot revive the retired owner on later thread-id turns.
- Restart mutation authority is the authenticated account-assignment and security-policy scope before model and service-tier eligibility. Model filtering constrains only replacement selection.
- Goal-restart retirement is an account-selection capability. An existing HTTP bridge cannot consume the request first through local reuse, durable-owner promotion, or forwarding. The retired owner is excluded from stale account snapshots for the remainder of the request, including when another selector wrote the scoped marker and this selector discovers it after losing the compare-and-set.
- Canonical bridge replacement preserves request-owned pre-submit admission on the detached predecessor, but that predecessor cannot publish new continuity aliases under the replacement's key. Every detached generation remains lifecycle-owned and capacity-counted until resource closure ends, including an idle predecessor already marked closed for admission.
- Drain status counts unsettled pending or queued work after detachment closes a generation for admission. If an idle predecessor alone fills the cap, the verified restart owns its bounded close synchronously and rechecks capacity before opening a replacement.
- Resource close is single-flight across reader retirement, account invalidation, and shutdown. Capacity is released only after resource finalization, not after detachment or a bounded-close timeout. Close finalization defers caller cancellation until owned resources are released, while shutdown starts all snapshotted closes before propagating cancellation and retains failed generations for a later close pass. Durable claims are fenced per websocket generation as well as per replica, so a replacement for a row still owned by the same configured replica advances the owner epoch before serving work even when model-transition isolation no longer uses that row for routing. Security-authorized rebind keeps typed continuity provenance so a source-qualified session-header tombstone cannot reappear as an untyped hard owner.
- Durable file pins, responses, conversations, live/durable bridges, replay, and reattach sources are independent hard evidence; conflicting evidence fails closed instead of using source precedence. Opaque file IDs with no live durable pin remain unpinned for compatibility with uploads that occurred outside the current process. A resolved file-pin owner bypasses the current-Codex thread PROMPT_CACHE row the same way it bypasses process-session locality, so an upload does not rebind later unpinned turns on that thread.
- Dashboard prompt-cache TTL is persisted in settings so operators can adjust it without restart.
- Background cleanup removes stale prompt-cache rows proactively, while manual delete and purge endpoints provide operator override.

## Constraints

- Historical sticky-session rows created before the `kind` column are backfilled conservatively to a durable kind to avoid accidental purge.
- Durable `codex_session` and `sticky_thread` mappings are never deleted by automatic cleanup.
- HTTP forbids CR/LF in headers and affinity parsing strips surrounding whitespace, while database text preserves LF. The internal soft-key sentinel therefore cannot be reproduced by a normalized client turn-state header.
- Every transport resolves live and durable turn-state aliases; an existing route or socket is not itself proof that a newly supplied conversation belongs to that account.
- File owner pins live in the shared application database. Cross-replica bridge forwarding still authenticates the origin-resolved owner, but the receiving replica must revalidate that owner against a fresh durable lookup.

## Failure Modes

- Cleanup failures are logged and retried on the next interval; request handling continues.
- Manual purge and delete operations are dashboard-auth protected and return normal dashboard API errors on invalid input or missing keys.
- Mixed-version replicas may temporarily produce both raw and namespaced rows. The raw row wins conservatively, which may reduce spillover but cannot weaken continuity.
- A raw process-session value may collide with an explicit turn-state value. Source-qualified abandonment lets the process session recover without making the retained raw account disappear from turn-state lookup.
- Partial file-pin coverage or conflicting hard-owner metadata returns a stable fail-closed error before upstream dispatch; zero file-pin coverage preserves the established opaque-ID forwarding path.
- A turn-state token learned from a retired WebSocket is discarded before a movable bare-session request connects to another account.
- An ordinary same-session request, or a goal-marked request that still carries previous-response, conversation, account-scoped file/image, or unresolved tool state, remains fail-closed on an unavailable raw owner.
- Local caps, retry exclusions, transient runtime health, and budget pressure never authorize legacy hard-owner abandonment.
- A live bridge may retain a detached ACTIVE account object after the database owner becomes unavailable. A verified goal restart bypasses that stale bridge and reaches guarded account selection; otherwise bridge reuse would strand the restart on the old owner.
- Selection inputs can predate the guarded retirement transaction. Once retirement succeeds, or once a compare-and-set loser rereads the winner's scoped marker, the old owner is filtered from those inputs so the request cannot immediately recreate namespaced affinity on it.
- A rolling older replica ignores the scope column. The scoped marker therefore leaves the historical timestamp tombstone empty, causing the older reader to keep the retained hard owner instead of treating the row as globally ownerless.
- Repeated restart replacement cannot hide visible or idle predecessor generations from the session cap or shutdown merely because a newer generation occupies the canonical key or the predecessor is admission-closed.
- Admission-closed pending work remains restart-blocking, while an idle predecessor that alone fills the cap is synchronously closed before replacement capacity is enforced.
- Account invalidation treats an owned/successful resource-close task, not the admission-only `closed` flag, as evidence that detached teardown is covered.
- A nested stream finalizer may clear a detached reservation before outer request cleanup runs, so final cleanup sweeps every detached generation for newly drainable ownership instead of relying on the mutable marker transition alone.
- A predecessor close may release after its same-replica replacement is created, including after a model transition clears the durable lookup from routing; generation-specific owner epochs prevent that stale release from closing the replacement lease.

## Example

A process session is mapped to account A, but A is locally capped. A self-contained request may run on account B while the process-session row continues to point to A. If B produces `resp_123`, a follow-up carrying `previous_response_id=resp_123` follows B's response-owner index. If the same follow-up also references a file pinned to A, it fails with `continuity_owner_conflict` rather than choosing either source. By contrast, a first-turn request carrying only an opaque `file_external` ID that has no live codex-lb pin remains eligible for ordinary routing and is forwarded verbatim.

For an explicit restart example, session `thread-1` has a raw legacy mapping to
quota-exceeded account A while account B is active. Codex resends the complete
account-neutral thread under `thread-1`, without previous-response or
conversation continuity, and includes its goal-continuation marker. The proxy
marks the still-current A mapping abandoned for process-session interpretation,
selects B, and records subsequent session/response continuity on B. An explicit
turn-state request using the same raw text still resolves A. If A recovers or
the row is rebound before the marker commits, the compare-and-set misses and
the request remains fail-closed.

## Operational Notes

No schema or setting migration is required for bare-session spillover. Namespaced rows appear lazily, and old raw rows age out only through existing operational controls. Rollback simply removes the spillover capability and leaves both row forms readable.

Goal-restart recovery adds no setting. Its nullable abandonment-scope migration
requires no backfill: a historical non-null timestamp with NULL scope remains
global, while `session_header` preserves an equal explicit turn-state owner.
Source-qualified markers leave the legacy timestamp NULL, so an older binary
safely restores conservative hard ownership during rollback. Dropping the scope
column loses only restart-recovery state; it does not make the retained owner
mobile.

## Policy-conflict retirement on the request path

The [policy-excluded owner requirement](spec.md#requirement-policy-excluded-continuity-owners-retire-only-when-durably-unavailable) uses the existing guarded durable retirement operation. Policy exclusion is a selection outcome, not proof that an account is dead. The repository checks current account state, reset horizon and the observed session identity before changing ownership scope.

For example, an unanchored continuation whose owner remains rate-limited for six hours can retire once and select a fresh account when the request has a much shorter budget. An active excluded owner or an owner resetting inside that budget stays bound. Client response anchors, file pins and same-owner-only full-resend proofs retain their ownership restrictions. Existing migrations, defaults and background abandonment grace periods remain applicable; there is no new setting.


## Child bridge idle retention on 2026-10-13

See [requirements](spec.md#requirement-child-http-bridge-idle-retention-follows-the-child-affinity-bound). Child sticky row expiration alone did not release a retained socket: thread bridges used the long Codex idle lifetime and prompt-cache bridges used their independent idle setting. Affinity now carries an explicit child idle cap so hard turn-state and process affinity preserve ownership while bounding resource retention.

Example: a short-lived child with a 3600-second cache setting retains an idle bridge for at most 300 seconds; a 120-second child cache setting gives at most 120 seconds. Reuse shortens an existing longer retention policy. Ordinary parent bridges retain their normal policy. Idle pruning continues to protect pending requests, reservations and admission waiters; this cap does not time out an active inference.

No new operator setting or schema is needed. The existing fixed child cap and shorter configured bounds supply the policy. Product-route tests cover creation, reuse, idle pruning and zero remaining account pressure; hard affinity and ordinary parent controls are covered separately. Live-provider and distributed-runtime evidence remain separate from local regression results.


## Deferred sticky reallocation, 2026-10-14

Operators can select `after_compaction` through `PUT /api/settings` with `{"stickyReallocationTiming":"after_compaction"}`. GET returns the stored value; an unrelated partial update preserves it. The compatible default is `immediate`. To revert policy, PUT `{"stickyReallocationTiming":"immediate"}`. This batch adds no environment setting or dashboard UI control.

Why this is optional: deferral keeps a warm, nearly exhausted account longer, trading immediate pressure relief for conversation locality. Changing the default would alter existing pool behavior. Timing is a behavior setting stored in the existing dashboard database and resolved through the existing routing snapshot; it is not a deployment-only or incident-debug variable. Public routes prioritize prompt-cache affinity, so changing only the internal sticky-thread flag would leave the requested policy unreachable there.

In deferred mode an active soft owner at 96 percent stays on account A for ordinary HTTP and native WebSocket turns; explicit compact can choose account B at 10 percent. Hard response/file/turn-state ownership still constrains compaction to its owner. Actual exhaustion and existing safe failure recovery continue to use their established paths. An arbitrary synthetic marker is not treated as an explicit compaction boundary.

Revision 20261014_000000_add_sticky_reallocation_timing adds a bounded, non-null column with the historical immediate default. Upgrade/downgrade/upgrade and schema drift are exercised on disposable SQLite, PostgreSQL 16 and MySQL 8.4. Downgrade removes this preference; a later upgrade initializes immediate again. No production migration or deployment was performed.

See [requirements](spec.md) and [verification](../../changes/archive/2026-10-14-repair-five-history-boundary-contracts/verification.md).

## Parent and child bridge reuse

Child idle caps apply when incoming affinity actually identifies child lineage. Applying a minimum on every reuse incorrectly shortens an ordinary parent turn-state alias after it has adopted the configured Codex lifetime. A parent bridge promoted from 120 seconds to a 600-second Codex lifetime therefore keeps 600 seconds during ordinary alias reuse; a recognized child still adopts its shorter effective bound. This affects idle retention, not active-request interruption or account ownership. Parent alias, API-key isolation and real HTTP child-reuse regressions cover the boundary. See [requirements](spec.md).
