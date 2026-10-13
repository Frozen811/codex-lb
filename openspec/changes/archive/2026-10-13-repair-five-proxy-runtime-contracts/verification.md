# Verification: five proxy runtime contracts

Local source: `7e3779ffaea1a27c29710a7d496e8fa037131f98` plus preserved working-tree changes, 2026-10-13. Exactly five rows were selected from 338 source records, initially **НЕ ПРОВЕРЕНО**. No commit, push, PR, merge, release or deployment is performed.

## Outcomes

| Registry row | Local result and proof | Limits |
|---|---|---|
| UP-PR-2561 | Fixed warm admission with a frozen pre-lock settings snapshot. Dashboard 128, unlimited zero, inherited null and lower-cap refusals cover keyed/unkeyed public HTTP routes and slash aliases. Unit cases exercise replica shares and updates; existing tests preserve fair share, owner authorization, held leases, cancellation and cleanup. | Replica shares are deterministic local simulations; live distributed admission and upstream deployment are not certified. |
| UP-PR-2308 | Fixed pool quota projection and privacy on direct HTTP, HTTP bridge, source SSE and both native WebSocket paths. Two actual SQLite account observations at 97/36 yield 66.5 percent. Raw account attribution remains 97; unknown families/pools are omitted, cache failure preserves inference, cancellation propagates. Public `/v1` streams still filter vendor events. | Synthetic upstreams and a local aiohttp source server; no live Codex/provider acceptance. |
| UP-PR-2112 | Existing HTTP timing correction independently verified. Public routes persist post-admission first-event, created and output timings; local events/keepalives cannot manufacture phases, observed zero survives and real errors with synthesized IDs count. Actual Prometheus observations and disabled-metrics controls pass. | Deterministic clock offsets describe correctness, not provider latency. |
| UP-ISSUE-2343 | Existing pending/drained/unknown observer independently verified. Four public HTTP cases return while real SQLite reservations remain reserved; loopback drain status reports pending with in_flight=0, then drained after exactly one finalization/log. Completed settlement callback handoff and malformed/unavailable observation controls pass. | Instantaneous process ownership is not an atomic stop certificate or historical durability audit. |
| UP-ISSUE-2505 | Existing grace/cleanup ordering independently verified on Windows units and real Linux process tests. Six immediate-ready SIGTERM starts and two held DB-operation barriers finish without pool-cancellation errors or unreleased leader ownership; grace expiry/deferring cleanup remain bounded and tracked. | Isolated local SQLite; PostgreSQL/MySQL and production shutdown are external. |

## Reproduction and verification

The pre-application public regressions produced **26 failures and 4 passes**: 12 warm-cap failures and all 14 original quota cases. [pytest-red.xml](pytest-red.xml) and [pytest-red.log](pytest-red.log) retain the actual failing envelopes and raw account payloads. The initial corrected scope then passed 59 tests.

Final aggregate: **352 PASS**, zero failures/errors/skips/xfails, across 12 full focused modules and 13 additional selected test functions. [Exact command](test-command.json), [pytest-final.xml](pytest-final.xml), [pytest-final.log](pytest-final.log). New test files contain 99 cases; they are part of the aggregate and are not counted again.

Linux process suite: **3 PASS**, zero failures/errors/skips/xfails. [linux-shutdown-final.xml](linux-shutdown-final.xml), [linux-shutdown-final.log](linux-shutdown-final.log). Two prior barrier passes overlap this suite. The total is **355 distinct passing cases**, not a sum of every intermediate run.

Linux used a disposable environment outside the checkout and an ext4 staging directory. All 774 application Python sources match the checkout after newline normalization, and the process-test source matches byte-for-byte ([stage verification](linux-stage-verification.json)). The only byte difference is restoration of the original line endings in request_submit.py; implementation text is identical. Original staged source checksums are retained in [linux-source-hashes.json](linux-source-hashes.json). The final command executes `tests/integration/test_shutdown_drains_database_tasks.py` with a 180-second test bound and the original five-second process-exit assertion. Telemetry is disabled for this rehearsal. No application database or live bot/service is substituted for test storage.

Earlier harness attempts are not product failures: the six-start run on the mounted Windows tree exceeded the aggregate test bound; the initial ext4 export omitted bundled configuration/pricing resources and failed startup. The completed export passed the unchanged process suite. The new reservation-observation fixture initially gated the handoff method rather than its detached finalizer, then used the wrong historical status spelling; gating the real finalizer and asserting the canonical `finalized` state fixed that fixture. The first broader run's four `/v1` expectations also incorrectly expected native telemetry on a public-contract stream. Public filtering was retained, and the corrected assertions are covered by the final aggregate.

## Static checks

- Ruff check and format check: all 14 changed Python files pass.
- `ty check`: changed application code and focused tests pass.
- Proxy architecture, cancellation safety and timing seams pass.
- Settings classification: 98/98, T0=13, T1=51, T2=0, T3=30, T4=4.
- Migration topology: 275 revisions, one head `20261010_000000_add_source_catalog_discovery`; no migration is added. Static migration safety passes and does not measure runtime.
- Simplicity budgets pass: README 218/225 lines and 10/10 headings; env 54/60 lines; core nav 5/5; unexpected tracked root entries 0.
- OpenSpec 1.11.0: strict change valid and strict canonical specs **68/68 PASS** ([change](openspec-change.log), [specs](openspec-specs.log)).
- `git diff --check`: exit 0 ([log](diff-check.log)); existing line-ending conversion warnings are retained.

The Windows aggregate retains Starlette/AnyIO deprecation and historical SQLite expression-index reflection warnings. Neither is a failed test or new production claim. Focused verification does not establish a green full repository suite.

## OpenSpec verification

Completeness: seven bounded tasks are complete. Correctness: all four delta requirements and their 14 scenarios are mapped to effective caps, settings cleanup, transport projection/privacy and existing compatibility tests. Coherence: fresh owner fences, usage ingestion, API-key finalization and public filtering retain their existing ownership. Stable normative changes and context are synchronized before archive. No critical implementation gap remains in this local change.

## Scope and preservation

The final batch diff was read in full against the initial checkout, including existing dirty content: [batch-existing-files.diff](batch-existing-files.diff). Exactly five source rows are changed and the other 333 are preserved. The initial 489 dirty files are recorded in [initial-manifest.json](initial-manifest.json); all 481 unrelated initial dirty files retain their hashes, and per-row readback is checked in [closure.json](closure.json). A Serena configuration auto-upgrade was restored to its exact initial bytes.

Existing partial records, F-045, CI-04, full-history/platform limitations and live client/provider/hosted CI/public/production scopes remain unchanged. These local closures do not merge the upstream PRs or attest their external rollout. Community implementation attribution: [UP-PR-2561](https://github.com/Soju06/codex-lb/pull/2561), [UP-PR-2308](https://github.com/Soju06/codex-lb/pull/2308).
