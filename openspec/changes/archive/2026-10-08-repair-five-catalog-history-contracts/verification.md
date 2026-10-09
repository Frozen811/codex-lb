# Five catalog/history contracts - local verification, 2026-10-08

Base: local main `005c8aa4d06be1d0d2f1ccdb2e0f90b725884f8e`. Initial working tree was clean. Exactly five initially unverified source rows: UP-PR-2445, UP-PR-2101, UP-PR-2085, UP-ISSUE-1467, UP-PR-2543. Fresh GitHub PR heads/descriptions and issue contents are retained in source-snapshot.json. No source closure is inferred from upstream status.

## Results by source

| Source | Local result | Evidence and boundary |
| --- | --- | --- |
| UP-PR-2445 | Repaired | Origin/backend-api plugin GET aliases and slash forms preserve status, bytes, repeated query parameters and pool credentials. POST aliases refuse dispatch; every alias is firewall protected. Remote marketplace/install acceptance is unverified. |
| UP-PR-2101 | Repaired, account-local scope | JSON body context.session_id has a hard, separately namespaced owner seeded from the existing soft process owner. Original bytes and native encrypted-argument/truncation headers survive. Pausing the owner fails closed; 401, quota/transport and refresh connection errors never dispatch to another account. Header-only compatibility retains existing behavior. Pooled history fan-out and live native decryption are outside this design. |
| UP-PR-2085 | Implemented | Captured Astra metadata was checked against the actual openai/codex rust-v0.153.4 models.json resource, SHA 698da6fb7a825cd3ede1696e4ce8579ef5c42c02. The instruction/model-message payloads are omitted from astra-captured-metadata.json. Bootstrap context/reasoning/code-mode/plan/speed fields and websocket preference are preserved. Both public HTTP Responses routes normalize Astra labels before controlled egress. Existing pricing snapshot is retained. |
| UP-ISSUE-1467 | Existing repair independently confirmed, catalog scope | An authoritative Pro catalog omitting Spark is serialized and persisted to isolated SQLite. Clearing the registry and using real startup reconciliation restores Spark in /v1/models, native models and /api/models. No further runtime change was needed; live entitlement and provider inference are unverified. |
| UP-PR-2543 | Existing repair independently confirmed, DOC/CONFIG scope | Shipped TOML and all inline TOML parse. API-key provider fragments have explicit native catalog URLs and the discovery feature after merging top-level feature settings as documented. Existing installed-client E2E requires macOS sandbox-exec and is skipped on Windows; current-client picker behavior is unverified. |

## Regression sequence

- `uv run pytest tests/integration/test_catalog_history_batch.py tests/unit/test_request_policy.py tests/unit/test_client_setup_examples.py -q --tb=short`: baseline 24 failures / 107 passes. Twenty-three failures exposed product gaps (plugin URLs, missing Astra/aliases, native object validation and cross-account 401 retry). One test initially treated a documented provider-only TOML fragment as standalone; corrected to use the documented merge. After runtime repairs: 131 passed.
- `uv run pytest tests/integration/test_catalog_history_batch.py tests/integration/test_api_firewall_middleware.py tests/unit/test_affinity_observation_source.py -q --tb=short`: 61 passed, including owner pause, native refresh failure and firewall aliases.
- `uv run pytest tests/unit/test_model_registry.py tests/unit/test_pricing.py tests/unit/test_pricing_catalog.py tests/integration/test_v1_models.py tests/integration/test_proxy_native_history_notes.py tests/integration/test_codex_plugin_catalog_passthrough.py -q --tb=short`: 433 passed / 1 failed. Failure was the old native bootstrap assertion that every model uses shell_command; captured Astra uses unified_exec. The assertion was updated specifically for Astra, preserving all other models.
- Fresh `uv run pytest tests/integration/test_v1_models.py tests/unit/test_model_registry.py -q --tb=short`: 173 passed after correcting that expectation. Pricing, native compatibility and plugin cases passing in the preceding aggregate retain their evidence; the failed aggregate itself is not reported green.
- `uv run pytest tests/unit/test_proxy_load_balancer_refresh.py tests/unit/test_affinity_observation_source.py tests/unit/test_request_policy.py tests/unit/test_client_setup_examples.py tests/e2e/test_codex_daybreak_profile.py -q --tb=short`: 208 passed / 4 skipped. Three existing T21 locking tests are skipped because their version-conflict premise no longer applies. Installed-client E2E is opt-in.
- `uv run pytest tests/unit/test_proxy_utils.py -q -k 'codex_control or sticky_key_for_codex_control' --tb=short`: 6 passed / 1465 deselected.
- `uv run pytest tests/integration/test_proxy_api_extended.py tests/integration/test_daybreak_capability_routes.py -q -k 'codex_control or thread_goal or plugin_catalog or native_history or native_notes or history_session' --tb=short`: 25 passed / 214 deselected.
- Final `uv run pytest tests/integration/test_catalog_history_batch.py -q --tb=short`: 34 passed. Spark was subsequently strengthened with a dashboard assertion; its final individual rerun passed.
- With `CODEX_LB_RUN_CODEX_PROFILE_E2E=1`, the installed-client E2E reports 1 skip specifically because this Windows host lacks the macOS sandbox-exec harness.

## Static and documentation checks

- `uv sync --frozen`; docs dependencies restored with `uv sync --frozen --group docs`.
- Whole-repository `uv run ruff check .`, `uv run ruff format --check .` (1499 files), and `uv run ty check`: PASS.
- Proxy architecture, cancellation safety, timing seams, settings tiers and migration topology scripts: PASS. Migration topology retains 272 revisions / existing single head; no migration was changed or added.
- `uv run python .github/scripts/check_simplicity_budgets.py`: PASS. No new setting, README section, env-example entry or dashboard navigation.
- CI-pinned `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict --no-interactive`: 68 passed / 0 failed.
- Strict active-change validation: PASS. Four capabilities synchronize five added requirements and one modified requirement, with 11 scenarios and stable contexts.
- `uv run --group docs mkdocs build --strict`: PASS.
- `git diff --check`: PASS; saved source-row closure is recorded in closure.json.

## Completeness, correctness and coherence

Each selected source has a bounded implemented or independently verified local result. The API regressions cover every new delta scenario; existing catalog tests retain authoritative-refresh controls. Shared affinity typing replaces duplicated literal domains. No unresolved implementation finding remains in this selected scope.

Graph discovery and direct traces established route/control/affinity/request-policy dependencies. The post-edit graph-enriched search retains old line metadata for some newly inserted symbols, so final source reads and runtime tests provide the authoritative change evidence.

## Residuals

Do not treat the initial 433/1 aggregate as green. Existing T21 skips and the macOS-only installed-client E2E remain explicit. Starlette/AnyIO emits an existing deprecation warning. Disposable SQLite fixtures can log the existing missing lifetime-lock shutdown warning; no production database was used.

No full-repository pytest, live provider/Codex Desktop picker, remote plugin install, PostgreSQL/MySQL runtime, distributed replica, cloud CI, public artifact or production certification. No commit, push, PR, merge, release or deploy was authorized or performed. Existing partial/F-045/CI-04 and external source scopes remain unchanged.
