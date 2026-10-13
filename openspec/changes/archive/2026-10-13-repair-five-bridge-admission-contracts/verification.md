# Five bridge admission contracts — 2026-10-13

Source HEAD: `7e3779ffaea1a27c29710a7d496e8fa037131f98` plus preserved local changes. Exactly five initially unverified records were selected: UP-ISSUE-2090, UP-ISSUE-1758, UP-ISSUE-1799, UP-PR-2303 and UP-ISSUE-1935.

## Record disposition

| Record | Result | Remaining boundary |
|---|---|---|
| UP-ISSUE-2090 | **Fixed and closed locally.** Successful late-anchor reconciliation now updates the local lease estimate as well as persisted quota. Deliberate late-anchor 429/401 errors pass through the ledger handler without becoming a persistence 502 or retiring a healthy session. | Synthetic durable-completion race, real isolated SQLite reservations and public HTTP paths; live client/provider acceptance is external. |
| UP-ISSUE-1758 | **Fixed and closed locally.** The failed-creation path cancels its captured running creator even after waiter completion. Replacement, protected handoff and self-task controls remain intact. Cooperative cancellation and delayed predecessors retain the existing durable ownership fences. | Local lifecycle and public ingress proof; cross-process and production load are external. |
| UP-ISSUE-1799 | **Verified and closed locally.** Existing stale closed-handoff recovery admits a fresh public request instead of repeatedly returning an incompatible-handoff 503. Existing anchored/wrong-owner protections remain covered. | The original reporter's deployment and exact unavailable incident payload are not reproduced. |
| UP-PR-2303 | **Verified and closed locally.** Existing continuous backlog passes remain fair and ordered, isolate optional writer failure and persist complete transcripts in both rows/chunks formats before terminal delivery. | The upstream PostgreSQL performance numbers and production speed are not certified. |
| UP-ISSUE-1935 | **Partially verified.** The fork classifies capacity correctly and applies bounded safe retry, cancellation/deadline and output/owner guards across direct HTTP, bridge and native WebSocket paths. | The original proposal also asks for unbounded retries and assurance that an active real Codex goal never blocks. Those claims are not implemented or proven. An ambiguous POST, visible output or opaque owner cannot gain replay permission from the capacity message. |

## Reproduction and corrections

The valid pre-fix unit report has **5 failures and 8 passes**: four missing creator-cancellation variants and one stale local anchored budget. Fixture construction errors found before that report were corrected before recording the behavioral red evidence; they are not product defects. The route red report has **4 failures and 4 passes**: all four quota-refusal paths returned a persistence 502 instead of the intended 429.

The first broader run had **239 passes and 2 failures** in historical late-creator tests. Those fixtures expected a predecessor to ignore slot cancellation without actually modeling delayed cancellation. Their fake creators now catch that cancellation and await the explicit release barrier. The original assertions that the predecessor cannot claim, publish over or release the winner remain unchanged. The corrected final aggregate passes both cases.

## Final verification

| Check | Evidence |
|---|---|
| Focused aggregate, seven full modules plus 83 selected existing node IDs, four isolated workers | **278 PASS**, zero failures/errors/skips/xfails; [pytest-final.xml](pytest-final.xml), [pytest-final.log](pytest-final.log), exact argv in [test-command.json](test-command.json). |
| Additional direct HTTP capacity slice | **11 PASS**, zero skips/xfails; [capacity-http-final.xml](capacity-http-final.xml). Two cases overlap the aggregate, so the total is **287 distinct PASS**, not 289. |
| New admission coverage | 15 unit cases and 22 integration cases are included in the aggregate. API-key reserve/release, auth/quota refusal, creator cancellation/replacement and stale handoff cover both `/backend-api/codex/responses` and `/v1/responses`, including their explicit slash aliases. |
| Real SQLite transcript burst | Both `rows_v1` and `chunks_v2` persist 320 ordered nonterminal events in bounded batches before the test releases the terminal, despite a 60-second ordinary flush interval. Stored replay contains all 321 events and a completed, complete spool. A barrier allows an initial partial batch, so 10 or 11 writes are valid. This is a functional drain test with a ten-second synchronization bound, not a throughput benchmark. |
| Static checks on all six changed Python paths | Ruff check, format check and ty PASS. |
| Repository guards | Proxy architecture, cancellation safety, timing seams, settings classification **98/98**, migration topology **275 revisions / one head**, migration static safety and simplicity budgets all PASS. Static migration checking does not measure migration runtime; no migration is added. |
| OpenSpec 1.11.0 | Strict change PASS and strict canonical specs **68/68 PASS**; [openspec-change.log](openspec-change.log), [openspec-specs.log](openspec-specs.log). |
| Preservation | Exactly five source-table rows updated; the other **333** remain identical. All **452 unrelated initial dirty files** retain their hashes. Existing content in the four intentionally extended Python files is reconstructed and hash-checked; both canonical spec/context retain their original byte prefix. [initial-manifest.json](initial-manifest.json), [closure.json](closure.json), [batch-existing-files.diff](batch-existing-files.diff). |
| Whitespace / scope | `git diff --check` PASS. No commit, push, PR, merge, release or deployment is performed. |

The final test reports contain the existing Starlette/AnyIO deprecation warning (once per worker). The isolated test shutdown may log that it did not acquire the production SQLite lifetime lock; test databases are disposable and never substitute an application database. Neither warning is represented as production evidence.

The additional command is `uv run --no-sync pytest -q tests/integration/test_proxy_transient_retry.py -k capacity --tb=short --show-capture=no --timeout=60 --junitxml=<change>/capacity-http-final.xml`. The aggregate's exact 83 selected nodes are also saved in [selected-nodeids.json](selected-nodeids.json). Intermediate 35-case usage and new-route runs overlap the aggregate and are not counted again. Failed initial reports remain distinguishable from final reports.

## OpenSpec verification

Completeness: all seven bounded tasks complete, with UP-ISSUE-1935's original proposal explicitly retained as partial. Correctness: both added requirements and all six scenarios map to running/completed-waiter cancellation, replacement/handoff/self controls, real conservative reservation growth, quota refusal and key invalidation tests. Coherence: cancellation is requested under the existing registry lock, cleanup retains its existing lifecycle owner, budget state changes only after successful reconciliation, and the ledger exception preserves only typed local pre-dispatch refusals. Existing genuine persistence failures and replay-safety policy remain authoritative.

There is no critical gap in this implemented local change. It does not close the entire original UP-ISSUE-1935 proposal. Specs and context are synchronized before archive; the bounded change can be archived without turning that partial source record into a closure.

## External limits

All runtime proof uses disposable local SQLite and synthetic upstream fixtures. Actual PostgreSQL/MySQL execution, distributed races, live provider/client goals, native helper execution, public artifact contents, hosted CI and production behavior are not established here. Existing partial records, F-045 and CI-04 retain their scopes. UP-PR-2579 dispatch-generation migration work was excluded before the exact selection and was not implemented or reclassified.
