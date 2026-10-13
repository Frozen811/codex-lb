# Verification: five dead-anchor contracts

Local checkout: `7e3779ffaea1a27c29710a7d496e8fa037131f98` plus preserved working-tree changes, 2026-10-13. Exactly five initially **НЕ ПРОВЕРЕНО** registry rows are selected. No commit, push, PR, merge, release or deployment is performed.

## Outcomes

| Row | Local result and evidence | Limits |
|---|---|---|
| UP-ISSUE-1921 | Invalid/stale anchors normalize through existing raw HTTP and native WebSocket policies. Public bridge regressions now preserve actionable initial and repeated dead-client-anchor rejection, followed by eligible full-history recovery. | Controlled upstreams; live Codex/Desktop and provider state are not certified. |
| UP-ISSUE-1707 | Fixed incidental reset timestamps preventing retirement of paused, deactivated or confirmed-unusable reauthentication owners. All HTTP bridge paths/slash aliases and keyed/unkeyed variants recover onto a healthy account after anchor-free full history. Actual quota states still wait for an in-budget reset. | Administrative/credential recovery requires its existing owner eligibility proof. Encrypted checkpoints and uploaded files remain account-bound. |
| UP-PR-2423 | Existing exact-owner conditional retirement independently verified; fixed repeat-client-anchor requests reverting to 502 when durable lookup masks an already-retired owner. Duplicate calls preserve the original marker. | Local SQLite locks and real marker state, not a native PostgreSQL/MySQL concurrency certification or an upstream PR merge. |
| UP-PR-2467 | Existing exact-match carrier cleanup independently verified; fixed its local submit-time tombstone 404 being transformed into an operation-fence 502 by outer transparent recovery. Public tests show both carriers cleared, tombstone retained, delta refused and complete full resend admitted. Successor/client-anchor/file-pin/cleanup controls pass. | Synthetic late-remote-verdict injection and local persistence; distributed rollout not certified. |
| UP-DISC-1864 | Existing canonical and parameterless invalid-ID normalization and full-resend recovery verified across both native WebSocket endpoints, raw HTTP controls and HTTP bridge entrypoints. | No claim that all historical causes or live long-running client incidents have been eliminated. |

## Defect reproduction

The valid pre-application run produced **5 failures / 3 passes**: three inside-budget repository horizon cases and two native HTTP path/alias cases returning retryable 502. [Raw log](pytest-red.log), [JUnit](pytest-red.xml).

After correcting the horizon, all 53 owner unit cases passed, but all 24 public-route cases exposed the second-request 502 regression. [Log](pytest-focus.log), [JUnit](pytest-focus.xml). The tombstone public-path test subsequently exposed the third gap: `bridge_continuity_persistence_failed` instead of the selected 404 when no operation had been dispatched. [Log](pytest-focus6.log), [JUnit](pytest-focus6.xml). These are separately fixed; they are not counted as final passes.

Earlier harness problems were corrected: two mistaken import/adapter names, assistant string normalization expectations, and assuming API-key enforcement from the service settings stub alone. The final keyed harness explicitly enables dashboard API-key enforcement and configures a real token limit. It verifies four settled reservations and exactly 52 charged tokens from two successful 26-token turns. The two refused requests charge zero. Disposable first-run dashboard bootstrap tokens in failure logs belong solely to the temporary test database.

## Final verification

**238 distinct pytest PASS**, zero failures/errors/skips/xfails. The three final groups have no duplicate test identities: **149 owner/session/new-route cases**, **54 tombstone/denied-anchor/file-pin cases**, and **35 existing public transport cases**. The 53 new cases (25 unit and 28 integration) are included in that total. [Machine summary](test-summary.json), [exact commands](test-commands.json).

- [Owner/routes log](pytest-final-owner.log), [JUnit](pytest-final-owner.xml).
- [Anchor/ownership log](pytest-final-anchor.log), [JUnit](pytest-final-anchor.xml).
- [Transport log](pytest-final-transport.log), [JUnit](pytest-final-transport.xml).

The final suites retain the existing Starlette/AnyIO deprecation warning. Test teardown may report that an in-process test SQLite engine lacks a lifetime lock; the temporary database remains isolated and is never substituted for application storage. No full-repository green or live runtime claim is made.

Ruff check, Ruff format and scoped `ty check` pass on the five changed Python files. Proxy architecture, cancellation safety, timing seams, settings tiers, migration topology, static migration safety and simplicity budgets pass. [Exact commands/results](static-final-results.json) and linked raw logs retain the evidence. No migration, setting, dependency or UI change is added. `git diff --check` passes.

Strict delta validation passes and strict canonical validation reports **68 passed / 0 failed**. [Change log](openspec-change.log), [specs log](openspec-specs.log). Three normative requirements with sixteen scenarios and stable context are synchronized while retaining canonical pre-batch byte prefixes.

## OpenSpec verification

Completeness: all seven bounded tasks are complete before archive. Correctness: the status/horizon requirement maps to the 25-case repository matrix and 24 public-route cases; actionable rejection maps to repeat/marker/full-history/key-settlement assertions and existing missing-owner/file-pin controls; submit-time retirement maps to four real HTTP path/alias cases plus the 54-case exact cleanup/tombstone/successor/file-pin selection. Existing 35 transport cases verify stale-ID privacy/classification, full-resend recovery and stricter ownership refusal. Coherence: conditional account/owner checks, request settlement, alias cleanup and upstream replay fences remain authoritative. No critical gap remains within this local change.

The graph was consulted and refreshed for discovery/impact. Some dynamic or nested relationships are not represented (the new local rejection constructor is not a graph node); the current source and full batch diff establish those relationships directly.

## Scope and preservation

[Initial manifest](initial-manifest.json) covers 543 files present in the initial dirty/untracked snapshot. Only five of those source files are changed by this batch: two application files, the canonical spec/context and the registry. The other 538 retain their exact hashes, including restored incidental Serena cache writes. The third application file and owner unit file started clean; a new integration module is added. [Code diff](batch-code.diff) and [complete existing-file diff](batch-existing-files.diff) are compared against pre-batch dirty contents or clean HEAD as appropriate and read in full.

[Closure](closure.json) verifies exactly five changed source records, the other 333 records unchanged and selected-row readback. Existing partials, F-045/CI-04 and public/cloud/production limits retain their status. Local closures do not attest upstream PR readiness, merging or deployment. Primary community references: [UP-PR-2423](https://github.com/Soju06/codex-lb/pull/2423), [UP-PR-2467](https://github.com/Soju06/codex-lb/pull/2467); [source metadata](source-metadata.json).
