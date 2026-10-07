# Verification: five upstream limit contracts

Date: 2026-10-07, Europe/Kiev. Baseline: `205e9c54bbab433c2621378e5c05a86f2fd253cb`, local `main`, initially clean worktree. The user authorized exactly five registry tasks and a local commit on `main`. All five source rows initially had `НЕ ПРОВЕРЕНО`; baseline registry SHA256: `c3cf81d49413bbce130959ff556f9f28d9bf1fb26cac8214df10f1609c697927`.

## Selected scope and evidence

Live source identities/statuses are saved in [upstream-source-snapshot.json](upstream-source-snapshot.json). Existing implementations were evaluated against their actual source scope; unrelated PR dependency/version changes are outside this batch.

| Record | Verified contract and result |
|---|---|
| UP-PR-2449 | Existing code-less usage-limit classification independently verified through real streaming routes: pool rotation, last-account and post-visible health, immediate usage refresh. Two additional bridge regressions confirm last-account health before/after visible output. |
| UP-PR-2439 | Finite client reset metadata survives exhausted retries and original status-bearing quota terminals survive a failed staged bridge replay. Fixed malformed reset terminal rendering: booleans no longer become 0/1, strings/non-finite numbers no longer raise conversion exceptions. |
| UP-PR-2440 | Fixed non-finite typed upstream reset parsing, preserving the other finite reset field independently. Existing HTTP bridge long absolute/relative reset persistence, owner retirement, direct WebSocket metadata, and keyed deferred health/settlement were independently verified. |
| UP-PR-2403 | Existing usage-vs-burst, classification precedence, and model-capacity exclusion truth tables independently verified. Corrected the normative claim that request errors can be reclassified from echoed usage-limit text; the real route negative control leaves both accounts active and never rotates. |
| UP-PR-2391 | Existing library verified: predicate/deprecated count precedence, failover outcome bounds, scoped observe-only exhaustion probe, canonical pool quota terminal, preserved last failure, deadline precedence, and probe failure containment. Its original PR is a library addition; full fleet-size/runtime certification is outside this closure. |

## Reproduced defects

Before source changes, the 26 new numeric-boundary cases produced **19 failures / 7 passes**. Failures included boolean `resets_at` becoming 0/1, string/NaN/infinity integer conversion exceptions, and non-finite values surviving typed parsing, including numeric strings.

The corrected product regression selection produced **4 failures / 3 passes** before source changes: NaN/infinity leaked into post-visible terminal JSON on both `/v1/responses` and `/backend-api/codex/responses`. The passing controls established boolean omission and request-error echo protection. After the fix this selection is **7/7 passing**, including valid relative reset persistence in real SQLite.

## Focused validation

These scopes contain **495 distinct passing cases**, no skips or xfails. Repeated red/green subsets are not added to this count.

| Command / scope | Result |
|---|---|
| `uv run pytest -q tests/unit/test_openai_errors.py tests/unit/test_proxy_errors.py tests/unit/test_failover_foundation.py tests/unit/test_pool_terminal.py --tb=short --show-capture=no` | 344 PASS |
| `uv run pytest -q tests/integration/test_proxy_transient_retry.py --tb=short --show-capture=no` | 135 PASS |
| Bridge/reset/settlement/direct-WebSocket targets listed below | 14 PASS |
| `uv run pytest -q tests/integration/test_http_responses_bridge.py::test_http_bridge_codeless_usage_limit_benches_last_account --tb=short --show-capture=no` | 2 PASS |
| Final new streaming regressions (`-k 'invalid_reset_after_visible or request_error_echoing'`) | 7 PASS, overlap with the 135 above |
| `uv run ruff check .` / `uv run ruff format --check .` | PASS, 1483 files formatted |
| Scoped `uv run ty check` on both source files and all three edited test files | PASS |
| `scripts/check_proxy_architecture.py`, `check_cancellation_safety.py`, `check_proxy_timing_seams.py`, `check_settings_tiers.py`, `check_migration_topology.py` | PASS; 98/98 settings, 272 migrations, single head; topology compares local `origin/main` |
| `.github/scripts/check_simplicity_budgets.py` | PASS |
| OpenSpec 1.11.0 strict change and strict main-spec validation | PASS, 68/68 main capabilities |
| `uv run --no-project --with mkdocs-material mkdocs build --strict` | PASS |
| Main/delta requirement comparison | Both complete requirement blocks identical |

The 14-case command selected these exact targets:

```text
tests/integration/test_http_responses_bridge.py::test_http_bridge_usage_limit_preserves_reset_and_retires_unavailable_owner
tests/integration/test_http_responses_bridge.py::test_v1_responses_http_bridge_preserves_rate_limit_metadata_in_429
tests/integration/test_http_responses_bridge.py::test_v1_responses_http_bridge_preserves_rate_limit_after_failed_precreated_retry
tests/unit/test_proxy_http_bridge.py::test_http_bridge_precreated_usage_limit_defers_keyed_health_until_settlement
tests/unit/test_proxy_http_bridge.py::test_release_reservation_drains_deferred_keyed_health_after_release
tests/unit/test_proxy_utils.py::test_websocket_event_upstream_error_preserves_metadata_across_error_shapes
tests/unit/test_proxy_utils.py::test_process_upstream_websocket_text_transparently_retries_precreated_usage_limit_failure
tests/unit/test_proxy_utils.py::test_process_upstream_websocket_text_preserves_previous_response_usage_limit
```

## Completeness, correctness, and coherence

Two normative requirements, seven scenarios are implemented and covered. Existing classification truth tables cover coded/code-less distinctions; new parser and rendering cases cover each invalid field and finite compatibility; real routes cover original quota code/message, strict JSON output, relative reset persistence, and request-content echo. Ownership, visible-output replay prohibition, and keyed health deferral use existing product regressions. The implementation adds a shared numeric guard and a typed-model validator without new settings, migrations, or dependencies. Main requirements are synchronized and stable rationale is in the capability context. No critical findings remain.

## Limits and preserved behavior

All upstream I/O is synthetic; account persistence and public ASGI routes are real local product paths. The bridge's failed pre-created replay without a status-bearing recognized quota envelope retains its existing fail-closed `502 stream_incomplete` terminal; it still benches the spent account. PR 2439's original-terminal preservation is specifically the status-bearing recognized quota case, not every status-less code-less failed replay.

The graph index correctly guided the existing pipeline, but its fast refresh did not expose the newly added numeric guard; current source, type checks, and runtime tests supply that coverage. Existing Starlette/AnyIO deprecation warnings remain. MkDocs was unavailable in the project environment; the strict build passed using an isolated tool environment without changing the lockfile. No full repository test suite, cloud CI, live provider, release, deployment, or production claim is made. Only the five selected source rows will change; registry readback and the other 333 rows' byte preservation are verified before commit.

Registry readback confirms exactly **5 changed source rows**, **333/333 other rows preserved byte-for-byte**, **338 total**, and **225 unverified**. The preserved-row SHA256 is `1a06d7f34e836b94a3ee72b9cd3226f0edd939e88f17fd7890102f0b57025176` before and after; initial selected rows and the comparison result are saved in [registry-preservation.json](registry-preservation.json). Scope counts: 106 local closures, 7 partial, 225 unverified.

The implementation commit is `6ca0f6f059a9dfaf26b69a582f2db7e2f75469c5`. The initial local-only scope above is historical: publication and successful exact-head cloud CI are recorded in [publication.md](publication.md). Its tested follow-up SHA `c50159869f3275f8f6c0541cabcc27cefeba68d1` passed CI #79, 35/35 jobs, plus the separate Windows, release-guard, and simplicity jobs (39/39 applicable jobs total).
