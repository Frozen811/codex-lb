# Verification: bridge cleanup, quarantine and paused delivery

Date: 2026-10-04 (Europe/Kiev). Base HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`. Exactly three source rows: UP-ISSUE-2270, UP-ISSUE-2268 and UP-ISSUE-2266. Local source only; no new commit, push, release or deployment.

## Results

| Row | Result | Evidence |
|---|---|---|
| UP-ISSUE-2270 | Repaired and locally closed | Four initial scheduled-path failures: a count change at the same timestamp was deleted, and a changed generation/epoch was reselected after a mixed batch deleted an unchanged row. Count fencing and keyset pagination preserve every changed candidate for the whole pass. Final 12 cases pass on each of SQLite, PostgreSQL 16 and MySQL 8.4, with batch sizes 1 and 128. Existing tombstone, continuity and recently claimed age controls also pass. |
| UP-ISSUE-2268 | Verified and locally closed for stale-clear ownership | Existing worker-wide generations, owner checks and early local-failure cutoff pass nine actual HTTP/WebSocket completion cases: a first failure during settlement, a replacement session, and a pruned/recreated replacement. Three route forms are exercised. Existing quarantine regressions pass. Overflow handling is not redesigned: active poison entries can exceed the nominal cap and weaker entries remain evictable under existing policy; no stronger bound or revised overflow policy is claimed. |
| UP-ISSUE-2266 | Repaired and locally closed for HTTP bridge delivery | Cancelled putter leakage, retained closed buffers, and closed sentinel cancellation reproduced as three initial unit failures. Real ASGI cancellation then reproduced retained output on all three routes; closing the response iterator exposed late reserved rows on canonical/slash v1 until the nested bridge iterator was explicitly closed. Final paused/resumed, stall, cancellation and writer-error route cases pass, with ordered output, exactly one failure terminal, independent request progress, zero queued bytes/pressure, settled reservations and active accounts. |

The upstream bodies were refreshed from [2270](https://github.com/Soju06/codex-lb/issues/2270), [2268](https://github.com/Soju06/codex-lb/issues/2268) and [2266](https://github.com/Soju06/codex-lb/issues/2266). Their GitHub state and original ISSUES.md author claims do not determine local completion status.

## Final commands

```powershell
uv run pytest -q tests/unit/test_bridge_cleanup_delivery_contracts.py tests/integration/test_bridge_cleanup_delivery_contracts.py tests/unit/test_http_bridge_event_queue.py tests/unit/test_downstream_delivery.py --timeout=25 --tb=short --show-capture=no
```

**82 passed**, no skips/failures: 18 new unit cases, 21 new real route cases, seven existing queue tests and 36 existing delivery tests. This command was run on final app source, including explicit REAL_SCHEDULER cleanup. One existing Starlette deprecation warning.

```powershell
uv run pytest -q tests/unit/test_proxy_http_bridge.py tests/unit/test_proxy_utils.py tests/unit/test_bridge_ring_lifecycle.py -k 'quarantine or paused_stream or detach or scheduled_purge or startup_cleanup_guard or completed_delivery or terminal_delivery or terminal_queue' --timeout=25 --tb=short --show-capture=no
```

**91 passed**, 2538 deselected, no skips/failures. Counts refer to separate focused commands and are not a full-repository aggregate.

For each disposable PostgreSQL 16 / MySQL 8.4 test database, using CODEX_LB_TEST_DATABASE_URL scoped to the command:

```powershell
uv run pytest -q tests/unit/test_bridge_cleanup_delivery_contracts.py -k scheduled --timeout=30 --tb=short --show-capture=no
```

**12 passed** on each backend, six unrelated tests deselected. These run the real leader cleanup method and database SQL; the change-before-delete interleaving is injected on the cleanup connection. They do not simulate independent database processes or certify every migration/backend contract. An earlier PostgreSQL attempt had six connection-refused setup errors after both disposable Docker containers exited; that attempt is not green evidence. Both were restarted, readiness confirmed and final commands passed. Test containers are removed after verification.

Scoped Ruff check and format pass for all five changed app files and three test files. `ty check` passes for the five app files. Proxy architecture, cancellation safety, timing seams, settings tiers and simplicity budgets pass. Timing seams initially required the explicit REAL_SCHEDULER argument; it was added and the check and final runtime command passed. Strict OpenSpec change validation and **68/68** main specs pass; two modified blocks and one added block are synchronized.

## Requirements and second manual review

| Contract | Implementation / coverage |
|---|---|
| Whole-pass scheduled purge fencing | Repository selected timestamp/generation/count predicates, ordered composite-key cursor; 12 scheduled cases per backend and existing age/continuity tests. Cursor memory is constant and batch size 1 proves progress after a zero-delete batch. |
| Quarantine lifetime / ownership | Existing quarantine clear and completion settlement; nine actual routes plus existing replacement/recovery/poison/local-strike tests. First local failure is retained even before reaching the quarantine threshold. |
| Queue byte/event accounting and release | Existing budgets preserved; Queue.shutdown clears detached payloads, removes blocked waiters, and ordinary producer cancellation propagates. Unit queue and route cancellation/writer-error tests cover release. |
| Saturated terminal handling | A graceful finish avoids an event-slot wait for None, preserving accepted success. A failed delivery retains already accepted output then emits one failure terminal outside the output slots. |
| Independent delivery deadline | Five-second fixed maximum, also limited by model idle allowance/request deadline. Unit test shortens only the fixed maximum while keeping the real two-hour allowance; actual routes use a short existing idle allowance. |
| Iterator and reservation ownership | DeliveryTracedStreamingResponse closes the suspended body via the existing cancellation-deferral helper. The bridge-or-retry wrapper closes its nested bridge stream explicitly. Three cancellation and three writer-error routes settle reservations; a repeated-cancellation unit test waits for cleanup before propagating cancellation. |

A second manual review checked ordering, count/version predicates, keyset comparisons, sentinel behavior, actual generator ownership, scheduler deferral, account neutrality, scoped test results, delta/main equality and preservation of previous edits. No subagent review is claimed. Exploratory detach/API cleanup edits were removed after identifying the missing nested close; request_submit.py is byte-identical to the saved pre-edit file and api.py has no new diff.

## Boundaries and preservation

The 32 MiB/4096-event budgets are per active stream. The existing lone oversized event exception remains; a blocked producer can retain the current event, and there is one pending failure terminal. This does not certify a fixed process-wide RSS ceiling, aggregate replay spool or native-helper memory. Existing quarantine overflow policy and UP-ISSUE-2271 crash/ABA residuals are unchanged. Hosted clients/providers, cloud gates, public artifacts, production and F-045/CI-04 remain separate.

Initial dirty/untracked paths: **110**. Only the retry repository, issues-check.md and owning responses spec/context overlap earlier dirty files; the other **106** must remain byte-identical. Prior repository receipt fix remains intact; original context is a byte prefix and original spec content outside the two modified requirement blocks is preserved. Exactly the three selected existing source rows receive status/evidence updates. Final source hashes and preservation evidence are in fingerprints.md.
