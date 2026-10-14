# Five owner, cursor and packaging contracts - local verification, 2026-10-14

Initial HEAD: cfc939cc69e6534996365a348b74eaf414283f34, branch main. Exactly five initially unverified source rows are owned: UP-PR-2591, UP-PR-2600, UP-PR-2098, UP-PR-2588 and UP-PR-2595. The checkout already contained 54 dirty/untracked files, including prior archived changes. No commit, push, PR, merge, release or deployment was performed.

## Completeness, correctness and coherence

| Dimension | Evidence |
|---|---|
| Completeness | Eight tasks completed; five source rows, four detailed cards and the synchronized summary updated and reread. |
| Correctness | Two added requirements cover original connect errors and cancelled SQLite cursor cleanup; all six scenarios have focused regression coverage. |
| Coherence | Existing failover budgets, health classification, API-key cleanup, task ownership, SQLite rollback, memory-engine construction and other backend configurations retained. No new setting or migration. |

| Row | Result |
|---|---|
| UP-PR-2591 | Fixed owner constraint passed only for model rejection. All required owners now preserve original connect failures, including exhausted 401 refresh attempts; movable requests retain failover. Four owner kinds (previous response, file, replay, turn state) preserve 429 and attribution in the actual connect loop. Native/public WS routes preserve 403/429/401 and release the selected stream lease exactly once; their existing unsupported slash variants close before account selection. Eight real HTTP bridge continuation cases cover 403/429 across public/native canonical/slash paths with a real imported SQLite account and original error envelopes. |
| UP-PR-2600 | Added weakly tracked SQLite cursor finalization and installed the factory through shared file-engine kwargs. Request/background cancelled RETURNING writes retain their traceback while an independent native writer succeeds after close. Custom cursor close errors do not suppress remaining cursor/native connection close; first error, rollback, weak lifetimes and repeated close verified. Real terminal batcher timeout plus shutdown drain works for rows_v1/chunks_v2; incomplete spool settlement, refusal of late append and subsequent leader acquisition succeed. |
| UP-PR-2098 | Existing implementation independently verified without another runtime edit. Both rendered default Compose configs publish only 2455; both configs with the explicit OAuth override retain 2455 and publish 1455 only on 127.0.0.1. Existing Docker examples, manual/device options and callback-port tests pass. Rendering does not start a callback listener or a container. |
| UP-PR-2588 | Existing urllib3>=2.8.0 floor from prior work independently verified in pyproject, lock, installed runtime and built wheel METADATA. Lock check passes offline; wheel dependency spec rejects 2.7.0 and accepts 2.8.0. No dependency file changed in this batch. |
| UP-PR-2595 | Moved misplaced normalizer documentation before executable statements and clarified SDK versus shared/native normalization. Runtime __doc__, inspect.getdoc and pydoc expose it. After removing string-only documentation nodes, the entire API module's executable AST is identical to its initial version. Stream fixtures, contract and API-key cleanup regressions pass; patched package metadata independently verified. |

## Reproduction and final test evidence

Before wiring the SQLite factory, retained-traceback tests reproduced database is locked for both file-engine roles. After adapting the upstream terminal harness to this fork's owned timeout task, both spool formats reproduced the same lock, and the existing owner-connect regression reproduced forbidden reselection and a generated owner-unavailable envelope. These failures disappeared after implementation. The final terminal harness uses the real batcher close/drain, not manual cancellation.

The connection factory and initial SQLite tests were inspected at upstream commit 66aaaa32f423bd28c85cae3950aa7cdedab404c9. This fork differs from that source: a persistence observation timeout retains its task until shutdown, so the integration regression explicitly exercises the existing owned shutdown drain. Early harness failures (missing lease acquired_at, unsupported WS slash routes and native HTTP's SSE response) were corrected to match existing contracts; they are not final product failures.

**412 distinct tests passed, two uvloop tests skipped, zero failures or xfails.** JUnit names were checked for duplicates across these disjoint final selections:

1. `uv run pytest -q tests/unit/test_db_session.py tests/unit/test_sqlite_connection.py tests/unit/test_docker_oauth_ports.py tests/unit/test_docker_networking.py tests/unit/test_installation_documentation.py --tb=short --maxfail=3`: 114 passed, 2 skipped, 14.07s. Skips are rollback/close variants of test_sqlite_worker_completed_during_loop_starvation_skips_reclaim[uvloop], because uvloop is unavailable on this Windows host.
2. `uv run pytest -q tests/unit/test_websocket_transport_fallback.py tests/unit/test_native_stream_fixtures.py tests/unit/test_proxy_upstream_fingerprint.py tests/unit/test_http_bridge_event_batcher.py --tb=short --maxfail=3`: 150 passed, 1.89s.
3. `uv run pytest -q tests/unit/test_proxy_utils.py -k 'connect_proxy_websocket or websocket_failover' --tb=short --maxfail=3`: 30 passed, 1450 deselected, 12.34s.
4. `uv run pytest -q tests/unit/test_proxy_api_responses_contract.py tests/unit/test_proxy_api_key_usage_share.py --tb=short --maxfail=3`: 96 passed, 0.98s.
5. `uv run pytest -q tests/integration/test_required_owner_connect_errors.py tests/integration/test_sqlite_terminal_timeout.py --tb=short --maxfail=2`: 22 passed, 26.02s.

The existing Starlette BlockingPortal deprecation remains a warning. Test storage is provisioned by tests/runtime.py before application engine imports; no application or production database was used. Six WS slash cases are intentional refusal coverage, not supported slash WebSocket aliases. Native HTTP bridge tests consume SSE; public HTTP bridge tests consume JSON.

## Static, package and specification evidence

- Repository Ruff check and format check passed on 1561 files. Scoped ty passed on app/db/sqlite_connection.py, app/db/session.py, app/modules/proxy/api.py and app/modules/proxy/_service/websocket/mixin.py.
- Proxy architecture, cancellation safety, timing seams, settings tiers, migration topology and static migration-duration guards passed. Topology remains 275 revisions with the existing 20261010_000000_add_source_catalog_discovery head. Runtime migration duration was not measured.
- `.github/scripts/check_simplicity_budgets.py` passed: README 218/225 lines, headings 10/10, env 54/60, nav 5/5, tracked root extras 0/0.
- `uv lock --check --offline` passed. `uv build --wheel --offline --out-dir <evidence>/wheel` produced codex_lb-1.25.1-py3-none-any.whl; urllib3>=2.8.0 metadata and version membership checks passed.
- Four `docker compose ... config --format json` renders passed and their port mappings were asserted. No Docker daemon startup/build or image security scan was performed.
- Strict change validation passed and canonical strict OpenSpec validation passed 68/68. Two canonical requirements and context docs synchronized by appending to their original content.
- Full batch diff reviewed and git diff --check passed. 50/50 unrelated initial dirty/untracked files remain byte-identical; prior changes in shared files and all 354 other source rows are preserved. Saved source-row readback and hashes are in closure.json. Queue remains 359 records: 208 locally closed, eight partial, two not applicable, 141 unverified.

Exact JUnit reports, aggregate duplicate audit, package/Compose/AST checks, initial shared-file copies and batch diffs are stored at C:/Users/ext/.codex/visualizations/2026/10/14/01a138c3-9a17-7f63-839d-45c37238a3f4/five-task-baseline/.

## Practical limits

Evidence covers local Windows/Python, real disposable file SQLite, rendered Compose and fake upstream transports. uvloop starvation variants remain skipped. PostgreSQL/MySQL execution, actual provider/Desktop traffic, distributed races, container builds and image scans, public packages, hosted current-head CI and production are not established here. Historical upstream states remain dated evidence. Existing partials and all unselected source records keep their prior status.
