## Context

See proposal.md for the five-row scope. The bridge already distinguishes client anchors from proxy-injected bookkeeping and uses conditional owner retirement with an account-row lock and a second status predicate in SQL. The Python precheck and SQL predicate currently apply reset timestamps to every unavailable status, although only quota states can automatically recover at reset.

## Goals / Non-Goals

Goals: correct that horizon interpretation and independently verify the existing retirement and invalid-anchor contracts at product entrypoints. Account-bound encrypted state and uploaded files retain ownership. Healthy/recovered owners, changed owners and real near-reset quota owners remain protected.

Non-goals: new recovery configuration, distributed rollout certification, live Desktop/provider testing or arbitrary history portability.

## Decisions

Use the same two quota statuses in the account-row precheck and the conditional SQL update. The existing lock and expected-owner predicates remain authoritative. Ignore incidental reset timestamps for paused, deactivated and confirmed-unusable reauthentication owners; do not erase their stored timestamps.

Reuse current explicit `bridge_previous_response_not_found` rejection and exact-match denied-anchor invalidation. Test public status/code/remedy, no unintended raw fallback, durable marker idempotence, full-history recovery, delta refusal and successor preservation. Use disposable test storage configured by tests/conftest.py before importing application modules.

A retired durable lookup intentionally masks its account ID, which makes the generic missing-owner branch run on repeated client anchors. Reuse a single local rejection constructor and recognize positive retirement evidence before surfacing that generic branch. A genuinely missing owner keeps the existing refusal; file-pinned requests keep their stricter ownership guards.

A submit-time tombstone can refuse before the request has a dispatched operation. Mark that refusal with existing typed local pre-dispatch provenance and preserve it before the transparent stale-anchor recovery gate. No operation reset or raw replay is authorized by that local verdict. Existing committed-stream terminal rendering and lifecycle finalization retain responsibility for delivery and settlement.

## Risks / Trade-offs

- A quota reset inside the request budget is valuable continuity: retain waiting for both quota statuses and cover null, expired, equal-deadline and future timestamps.
- A sibling can recover/rebind ownership: retain account locking, SQL status conditions and exact-owner checks, and run existing race regressions.
- Historical reports include unavailable live context: local closures certify controlled public-route behavior; live-provider, multi-replica and client acceptance remain explicit limits.

## Migration Plan

Application-only change; no migration or setting. Deployment is outside this task.
