# Usage Refresh Policy Context

## Purpose

This context explains how codex-lb derives an account's usage and status, and
how to diagnose disagreements between codex-lb and Codex Desktop or the Codex
CLI quota pill.

codex-lb treats `/wham/usage` as the source of truth for account usage. Other
OpenAI account surfaces can display reset state earlier than `/wham/usage`,
especially during team reset windows, so the dashboard can temporarily show an
account as `rate_limited` even when Codex Desktop says the quota has reset.

## Access and refresh eligibility

A permanent refresh-token failure marks an account `reauth_required` and stops
proactive exchange of that refresh material, while ordinary requests may keep
using the stored access token until its known expiry. Claimless forced refresh
first reads current state: it adopts genuine peer rotation, uses fresh ciphertext
as the guard for unchanged non-terminal material, and fails closed without
exchange when terminal material is unchanged. Before access-token expiry, a
request that reaches this terminal failure may fail over after excluding the
account locally; it does not globally de-route it or move owner-bound continuity
to another account. At known expiry, selection and bridge reuse reject the
account before upstream I/O.

## Upstream Usage Source

codex-lb refreshes account usage by calling:

```http
GET https://chatgpt.com/backend-api/wham/usage
```

The call is made per account on the configured refresh tick, which defaults to
60 seconds. The client lives in
[`app/core/clients/usage.py`](../../../app/core/clients/usage.py), and the
scheduler lives in
[`app/core/usage/refresh_scheduler.py`](../../../app/core/usage/refresh_scheduler.py).

## Status Derivation

The fetched usage is fed through
[`apply_usage_quota`](../../../app/core/usage/quota.py), which derives account
status from `primary_window.used_percent`:

- `secondary_used >= 100`, regardless of `primary_used`: `QUOTA_EXCEEDED`
- `used_percent >= 100` on the primary rate-limit window: `RATE_LIMITED`
- `used_percent < 100`: `ACTIVE`

There is no manual reset step inside codex-lb. Recovery is driven by the next
refresh tick that observes a sub-100 value from `/wham/usage`.

## Why Codex Settings Can Disagree

Codex Desktop's Settings -> Account view and `/wham/usage` are fed by different
OpenAI-side data sources:

- `/wham/usage` exposes the rate limiter's internal counter. It updates lazily,
  typically on the next chargeable request through that account, or when its
  internal window crosses `reset_at`.
- Settings -> Account is fed by a separate account/quota view that often picks
  up team-side reset events earlier.

During a reset window it is normal for Settings -> Account to show the reset
state while `/wham/usage` still returns `used_percent: 100` for a short period
afterwards. codex-lb mirrors `/wham/usage` during that window, so the account
stays `RATE_LIMITED` or `QUOTA_EXCEEDED` until upstream catches up.

## Limit Warm-Up Exhaustion Threshold

Reset-confirmed limit warm-up compares the usage sample from before a refresh
with the sample written after that refresh. The pre-refresh sample must be at
or above the configured exhausted threshold, the post-refresh sample must be
below `100`, and `reset_at` must move forward.

The exhausted threshold defaults to `99.0` because some upstream usage payloads
plateau at 99 percent for windows that are practically exhausted. This avoids
missing reset-confirmed warm-ups for those accounts while keeping the reset
confirmation requirement intact. Operators who want the historical strict
behavior can set the threshold to `100.0`.

## Operational Notes

- Wait first. The next request through that account usually wakes the upstream
  rate limiter; codex-lb auto-recovers on the next refresh tick after the
  upstream payload changes.
- The dashboard Force Probe action fires one minimal `responses.create` against
  the selected account and immediately refreshes its usage. The probe uses a
  one-dot prompt and closes the stream after response headers. It omits
  `max_output_tokens`: the Codex Responses endpoint now rejects that field at
  any value. For example, a probe with `max_output_tokens=16` returned HTTP 400
  with `Unsupported parameter: max_output_tokens`, while the same request
  without the field returned HTTP 200. An accepted 2xx probe
  also contributes to that replica's probing-health recovery streak; non-2xx
  results do not restore routing health. Settlement reloads and normalizes
  weekly/monthly and zero-primary-capacity usage like ordinary routing and is
  discarded when newer replica-local health evidence arrives during that
  snapshot load; lease-only activity does not invalidate it. The account and
  usage rows are copied before the read session closes because rollback
  expires ORM attributes even with `expire_on_commit=False`. For example,
  an HTTP 200 probe with healthy usage must advance the local recovery
  streak after session teardown, rather than only returning a successful
  dashboard response while settlement logs an expired-row error. The earlier `16` floor addressed
  [#1895](https://github.com/Soju06/codex-lb/issues/1895) when upstream still
  accepted the field; warmup/compact-404 is a separate path.
- Do not manually flip the codex-lb account state to `ACTIVE` while
  `/wham/usage` still reports the account as fully used. That only masks the
  upstream state and can route traffic back to an account that the upstream
  limiter will reject.

## Verification Example

To confirm that the disagreement is upstream rather than codex-lb's mirror,
call `/wham/usage` directly with the same account token codex-lb is using:

```bash
ACCESS_TOKEN=...
ACCOUNT_ID=...   # chatgpt-account-id UUID, not codex-lb's id

curl -s https://chatgpt.com/backend-api/wham/usage \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "chatgpt-account-id: ${ACCOUNT_ID}" \
  -H "Accept: application/json" | jq '.rate_limit'
```

If `primary_window.used_percent` is still `100` here while Settings -> Account
shows the account as reset, codex-lb has nothing fresher to mirror. The account
is inside the upstream propagation window, and the practical fix is to wait or
use the Force Probe action. Check its `probe_status_code`: a non-2xx response
does not count as evidence that the account is healthy.

## Related Work

- [#676 - initial bug report on `/wham/usage` vs. Settings UI divergence](https://github.com/Soju06/codex-lb/issues/676)
- [#677 - dashboard per-account force-probe action](https://github.com/Soju06/codex-lb/issues/677)

## Usage-share evidence freshness

The estimate requires a fresh, complete canonical long-window row for every account contributing capacity. Monthly-capacity plans use the latest authoritative shape: monthly evidence, or a later weekly-duration quota explicitly reported in the primary slot. An ordinary lingering secondary row never substitutes for monthly evidence. Incomplete evidence fails open and reuses `UsageUpdater.request_refresh`, including its debounce and singleflight behavior. Each request wakes at most one account; the staggered scheduler covers the rest of a large pool.

## Reset evidence after live ingestion

[Issue #1975](https://github.com/Soju06/codex-lb/issues/1975) exposed a missed warm-up when live usage recorded a reset before a freshness-skipped poll. The [reset-evidence requirement](spec.md#requirement-persisted-current-reset-evidence-survives-a-skipped-poll) covers that path.

The scheduler locates the first retained observation of the current reset identity and reads that history span plus its predecessor. This survives restart and delayed deadlines without another consumption table. Existing warm-up claims consume pending, succeeded, failed and skipped attempts; a crash after claiming does not authorize another send. Current snapshots govern availability, while the historical pair proves the reset. Other warm-up triggers still require a poll write.

For example, live ingestion can record weekly usage falling from 51% to 0%, then receive more snapshots before the scheduler runs. The earlier pair remains usable even though the latest two rows show the same reset deadline. An expired or superseded identity is not replayed, and a missing predecessor supplies no proof.

The first-reset lookup can scan retained history for the selected account/window, and the following span is not row-capped. Already-claimed windows skip this lookup. This cost avoids discarding evidence at an arbitrary time or row limit; no new setting or migration is required.

## Pooled reset-credit target identity

The [cross-account target requirement](spec.md#requirement-cross-account-reset-credit-consumption-requires-target-identity) covers Codex consume requests whose explicit credit ID or `default`/`auto` choice belongs to another account. The caller must authenticate as ChatGPT, and the refreshed target needs its own ChatGPT account ID. A missing or empty target ID returns the normal 401 OpenAI authentication envelope, consumes no credit, keeps the observed credit snapshot, and starts no post-redemption usage refresh.

For example, caller A can select a cached credit on B, but B's missing workspace identity cannot be replaced with A's identity or an omitted upstream account header. These consume routes have no API-key usage reservation: refusal preserves the credit snapshot rather than settling a token reservation. The canonical `/api/codex` and backend WHAM/Codex aliases, with and without trailing slashes, use the same refusal. Tests use inert upstream stubs and never redeem real credits.

## Business Pro Lite alias

The upstream identifier self_serve_business_prolite is an alias for the existing prolite tier, including mixed case and surrounding whitespace. Keeping one canonical stored value aligns dashboard capacity, rate-limit metadata, and Pro-equivalent model eligibility without introducing a second plan.

For example, a workspace-less team account may receive that alias on a usage refresh and persist prolite plus its usage rows while retaining identity and encrypted credentials. A conflicting workspace still refuses the payload; an unknown plan still follows the existing identity guard. Local recorded HTTP and fresh-session SQLite evidence is in the archived 2026-10-03 verify-plan-json-metrics-contracts change. See [the canonical compatibility requirement](spec.md#requirement-canonical-business-pro-lite-plan-compatibility); the checks do not establish live provider plan capacities or change the existing operator override contract.


## Independent capped SQLite history verification (2026-10-04)

Capped reads bypass the full-history cache and preserve account cutoffs, timestamp/ID ties and all explicit recent-floor samples. Negative LIMIT means unlimited in SQLite; invalid cap values now fail before backend selection. Zero is valid. For example, cap 64 plus 18 recent samples returns 82 snapshots; a floor covering the full cutoff intentionally exempts all samples. The dense fixture contains 100,000 rows and returns 1,280 snapshots across 20 accounts. Dashboard numerical parity is checked separately. Local SQLite evidence does not certify PostgreSQL or process-wide RSS. See [verification](../../changes/archive/2026-10-04-verify-sqlite-history-reports-transcript/verification.md).

## Sliding idle warmup cycles (2026-10-05)

See [the stable-cycle requirement](spec.md#requirement-sliding-idle-warmup-claims-use-the-stable-cycle). Scheduling and durable claims must agree on which cycle is consumed. Using a moving upstream deadline as the claim key permits a second send after that deadline moves beyond jitter tolerance, even though slot timing still refers to the original stable epoch cycle.

For a 300-minute epoch cycle starting at E, account index 1 of a three-account pool has a slot at E+6000. Sliding samples at E+6000 and E+6121 both consume the claim ending at E+18000; the next cycle consumes E+36000. Fixed deadlines retain their own phase. Slot zero only adopts the epoch phase when consecutive observations show deadline movement matching elapsed observation time; treating every newly opened fixed window as sliding would suppress its first slot.

No settings, schema revisions, or opt-in defaults change. Existing idle thresholds, freshness, cooldowns, safety-state filters, and selected-account scope remain applicable. Old moving-deadline claims may differ from a first stable claim after upgrade; existing cooldown bounds that transition. SQLite service/repository controls cover all three slot indices and 180/300-minute windows. Live reset recovery is independently verified through ingestion, scheduler restarts, duplicate workers, failed/skipped/pending claims, and fresh-poll skips. See [local evidence](../../changes/archive/2026-10-05-repair-warmup-fallback-and-reset-evidence/verification.md); provider and distributed database execution remain outside this run.

## Workspace-specific refresh failures

The [refresh exclusion contract](spec.md#requirement-workspace-exclusion-preserves-other-records-during-refresh) uses the same exact permanent-failure code policy as request routing. The identity does not substitute for the selected routing record's ID.

For example, two records sharing a user identity can have different workspace availability. A refresh rejection of A leaves B active; refreshing B does not revive A. Bare payment-status responses do not justify permanent status updates. This repair does not add a workspace-discovery mechanism or change credential storage.
