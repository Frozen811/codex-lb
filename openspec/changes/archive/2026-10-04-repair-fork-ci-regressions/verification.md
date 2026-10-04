# Fork CI repair evidence

Date: 2026-10-04, Europe/Kiev. Local base: e03f212a1350b71c1a7d5badd065d7dc0e9d6b45; published fork main before repair: 94c9a8c24cc0dfdd4c5bce00aa1c46e6bc9d9b6d. User explicitly authorized diagnosis, repair, a new commit and fully successful CI; publication to fork main is required to obtain that evidence.

## Historical exact-SHA diagnosis

| SHA / run | Primary failures |
|---|---|
| 94c9a8c24 / [CI 37209560169](https://github.com/Frozen811/codex-lb/actions/runs/37209560169) | ty: 75 diagnostics in recently added tests. Rust wire: zstd request bytes parsed as plain JSON. MySQL and integration-core-3: explicit capability route inventory lacks three slash aliases. Integration-bridge: four stale WebSocket error assertions. Integration-core-1: job cancelled at its 20-minute deadline with continuous progress to 75%. Both aggregate checks correctly failed. |
| 8f713d322 / [CI 37208342573](https://github.com/Frozen811/codex-lb/actions/runs/37208342573) | Same ty and route-inventory failures. Other running jobs were cancelled by the subsequent main push; the run is incomplete. |
| 282ce1470 / [CI 37110799276](https://github.com/Frozen811/codex-lb/actions/runs/37110799276) | Same route-inventory failure in MySQL/core-3 and timed-out core-1. |
| 282ce1470 / [Windows 37110799272](https://github.com/Frozen811/codex-lb/actions/runs/37110799272) | Installed-wheel readiness/assets succeeded, but temporary-directory cleanup failed with WinError 32 on server.log. Current launcher already terminates the Windows process tree. The same source passed later [Windows 37208342443](https://github.com/Frozen811/codex-lb/actions/runs/37208342443) and [Windows 37209560182](https://github.com/Frozen811/codex-lb/actions/runs/37209560182); current exact-head smoke remains required. |

The GitHub API supplied run, attempt, job and logs evidence. Redirected log downloads were fetched without forwarding the PAT to the storage host. Raw logs remain outside the checkout; this report retains only the relevant diagnostics and public job identities.

## Local reproduction and repair

- Route/WebSocket selection reproduced **5 failed, 8 passed**. The route inventory now explicitly classifies backend/v1 search slash aliases and the individual-model slash alias. Four WebSocket assertions now preserve the exact authored quota error, status and message as required by responses-api-compat; original no-reconnect/no-second-account/no-replay assertions remain.
- Complete `uv run ty check --output-format concise` reproduced **75 diagnostics**. Test fixes use concrete SQLAlchemy Table typing, positive optional/payload narrowing, typed mock casts and a real Event subclass. No file exclusion, ignore, weakened ty rule or assertion removal was added.
- The native routed probe reproduced a UnicodeDecodeError on both direct and routed zstd bodies. It now verifies both Content-Encoding headers and decompresses both bodies before retaining model/input/native-helper assertions.
- The CI core shard limit is **40 minutes**, bounded. Per-test timeouts, stall detection, selected test files and required aggregate dependencies are unchanged. Current complete partition validation includes **202 integration-core files** across three shards.
- No production code or schema changed. Historical Windows cleanup was diagnosed; the current implementation is retained for fresh cloud verification rather than changing a currently passing launcher on assumption.

## Local verification

- `uv run ty check --output-format concise` — PASS for the complete configured tree.
- `uv run ruff check .` and `uv run ruff format --check .` — PASS; 1458 files formatted.
- Route/WebSocket failing selector — **13 passed**, 331 deselected, 15.49 s.
- Bridge cleanup/claims/backlog/terminal provenance and real direct-WebSocket/retry contract files — **98 passed**, 30.88 s.
- Fork publication, delivery, plan/JSON, telemetry/key and projection-history contract files — **237 passed**, 108.55 s.
- Actual freshly built native helper with the complete CI wire selection (`test_native_routed_egress.py`, `test_native_sse_egress.py`, `test_native_websocket_events.py`, `test_native_usage_egress.py`, `test_native_egress_helper_large_payload_ipc.py`) — **364 passed**, 44.00 s, no skips. Build: `cargo build --locked -p codex-lb-egress-worker --bin codex-lb-native-egress`, toolchain 1.96.0.
- Shard partition, architecture, cancellation, timing seams, settings tiers, migration topology and simplicity budgets — PASS.
- Strict OpenSpec change validation and **68/68 main specs** — PASS; the CI contract and stable context are synchronized.
- `git diff --check` — PASS.

Focused selections are separate from cloud full-suite evidence. The harmless warning is Starlette's deprecated BlockingPortal alias. Local tests do not prove PostgreSQL/MySQL or exact-head cloud completion.

## Cloud verification

Published repair: **575c18f4e55ab1138086523cc81edf00c03bfb4b**, [CI run 37224667796](https://github.com/Frozen811/codex-lb/actions/runs/37224667796), attempt 1, push to fork main. The completed GitHub API evidence confirms **29/29 CI jobs successful**, including all three core shards, the integration-core aggregate, CI Required, native wire, complete ty, both database test jobs, frontend, Docker, Nix, Helm and migration checks. Full bridge selection: **414 passed**, 420.43 s. Windows Startup Regression, release guards and simplicity budgets also completed successfully for the same SHA. The only skipped workflow entries are the expected upstream-only release/beta automation.

Machine-readable exact-SHA job identities, results and public links are saved in [cloud-ci.json](cloud-ci.json). The cloud results were reread independently after the watcher completed, including the run head SHA, total job count, success of every required aggregate and mandatory side workflow. CI-01 is closed for this verified source snapshot. Unrelated F-045/CI-04 platform stability, published release artifacts, deployment and provider traffic remain outside this CI repair.

A subsequent documentation-only commit records this evidence and archives the verified change; its main-push checks must also be observed before the final task report. Historical and source-code verification records above remain pinned to their actual tested SHA.
