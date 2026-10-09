## Scope and cloud reproduction

The complete pending work was published as `02f48bbca33a8e9c6a9332c437f7ed44d7543820`. GitHub had disabled fork workflows, so no checks started for that push. After the owner re-enabled Actions, the tree-identical trigger commit `f45df165201578645c13413a768244148a0f6613` started [CI #90](https://github.com/Frozen811/codex-lb/actions/runs/37943886023).

CI #90 finished with 26 successful jobs and nine failed jobs: six test jobs and three aggregate gates. The six test failures shared four underlying causes. Windows startup, PostgreSQL, frontend, Docker/Trivy/SARIF, Rust, Helm, Nix, migrations, lint, typing, and OpenSpec passed. A successful overall CI result is not claimed for that run.

## Red-before evidence

- Alpha-search's explicit fake rejected the newly forwarded `body_session_id` keyword.
- The exact capability inventory omitted four registered plugin aliases.
- Eight auto/WebSocket serialization cases incorrectly required the original JSON whitespace or escaped-key spelling. Raw HTTP cases already passed; parsed values matched on both transports.
- The coded-429 owner-bound fixture contained only encrypted reasoning, which the published quota exception now permits to fail over. Its expected `action=surface` log contradicted that premise.

Local reproduction of alpha-search and the usage serialization selection produced nine failures and 16 passes. The separate owner-bound/inventory selection reproduced two failures. All four roots were reproduced before their test updates.

## Completed local checks

| Command / selection | Completed evidence |
| --- | --- |
| `uv run --no-sync pytest -q tests/integration/test_proxy_api_extended.py tests/integration/test_daybreak_capability_routes.py tests/integration/test_catalog_history_batch.py --tb=line --show-capture=no` | 278 passed |
| `tests/integration/test_usage_generation_contracts.py` in the 77-case focused selection | All 75 usage/generation cases passed; that intermediate selection had 76 passes and one failure in the temporary response-anchor owner fixture |
| `uv run --no-sync pytest -q tests/unit/test_proxy_utils.py -k 'burst_429 or coded_429' --tb=line --show-capture=no` after the final tool-continuation fixture | 13 passed, 1458 deselected |
| `uv run --no-sync pytest -q tests/unit/test_routing_ownership_batch.py tests/integration/test_routing_ownership_batch.py --tb=line --show-capture=no` | 79 passed |
| `uv run --no-sync ruff check .` and `ruff format --check .` | Passed; the final four-file recheck also passed |
| `uv run --no-sync ty check` | Passed |
| `npx --yes @fission-ai/openspec@1.11.0 validate align-published-contract-regressions --type change --strict --no-interactive` | Passed with the explicit test-only `skip_specs: true` opt-out |
| `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict` | 68 passed, zero failed |
| `git diff --check` | Passed |

The final verified selections cover 445 distinct passing cases. The initially passing alpha-search case overlaps the completed 278-case route selection and is counted once. The temporary response-anchor fixture failed before reaching the intended error path; the final independent tool-state fixture passed all 13 burst controls. No intermediate aggregate with a failure is presented as green.

## Completeness, correctness, and coherence

| Dimension | Assessment |
| --- | --- |
| Completeness | All six tasks completed; four planned test files changed. |
| Correctness | Full control arguments are asserted; exact route inventory and policy disjointness remain enforced; aliases receive capability-denial coverage; HTTP bytes and canonical WebSocket SSE framing are asserted; usage, timing, cost, reservation, reports, and hard-owner isolation remain checked. |
| Coherence | Existing Responses bridge relay and account-ownership requirements are retained. No production code, schema, configuration, dependency, or normative requirement changed. |

No critical or warning issue remains in the local test-only change. Delta specs are deliberately absent because the implementation and normative contracts are unchanged. The original publication preservation manifest still matches 154 of its 155 paths; the sole intended difference is the owner-bound test in `tests/unit/test_proxy_utils.py`. All original runtime files remain preserved.

## Remaining scopes

Local checks authorize archiving this verified test-only change. Publication must still receive a complete successful CI matrix and Windows startup workflow on its exact new SHA. Existing provider, public-artifact, production, and distributed runtime residuals in the five original repair batches remain unchanged.
