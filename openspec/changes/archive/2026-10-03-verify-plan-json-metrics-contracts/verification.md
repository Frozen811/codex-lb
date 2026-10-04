# Verification: UP-PR-2512 / UP-PR-2515 / UP-PR-2529

Date: 2026-10-03. Base HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`.

## Findings and corrections

| Item | Product evidence | Result |
| --- | --- | --- |
| UP-PR-2512 | Three import variants; five real HTTP usage refresh scenarios; fresh database sessions and dashboard reads | Existing alias fix confirmed. Canonical prolite, original identity/ciphertexts, default 1125/37800 capacity, Pro-equivalent eligibility, unknown-plan and workspace refusal preserved. |
| UP-PR-2515 / F-057 | 48 Chat route variants, each with two turns, recorded actual HTTP upstream bodies; string/object response_format and text.format, both instruction roles, text/parts, stream/non-stream, canonical/slash requests | Before repair: 16 failed, 40 passed in the combined new suite. All failures were equivalent text.format losing the JSON instruction. Shared format detection repairs that path; developer role, content/order, non-JSON hoisting, and prefix stability verified. Slash variants exercise existing redirects with follow_redirects=True, not a claim of redirect-free aliases. |
| UP-PR-2529 / F-058 / F-059 | Four real CLI subprocesses: text/JSON × info/debug, primary and metrics listeners, log path with spaces; independent unit checks for 200/503 tuple decoding and tracing diagnostics | Original metrics Config is already logging-neutral. Before formatter repair: info-JSON produced null access fields; debug-JSON failed to start due recursive tracing lookup. After repair: four subprocesses pass, actual client/request/status retained, userinfo redacted, stream/file access records identical, no logging errors or recursion. |

## Final focused validation

- `uv run pytest -q --tb=short tests/integration/test_plan_json_contracts.py tests/unit/test_chat_request_mapping.py tests/unit/test_openai_requests.py tests/unit/test_prompt_cache_key_derivation.py tests/integration/test_proxy_chat_completions.py` — **376 passed**.
- `uv run pytest -q --tb=short tests/unit/test_plan_types.py tests/unit/test_usage.py tests/unit/test_usage_updater.py tests/unit/test_metrics.py tests/unit/test_cli.py` — **253 passed**.
- `uv run pytest -q --tb=short tests/unit/test_structured_logging.py tests/unit/test_otel.py tests/unit/test_runtime_logging_loop_handler.py` — **146 passed**, one optional uvloop module skipped.
- `tests/integration/test_metrics_server_logging.py` — **4 subprocess cases passed** after the runtime formatter correction (part of the initial focused logging command). Later changes to the two tuple-test fixtures only aligned their redaction expectation with the established INFO URL-userinfo contract; they changed no production/subprocess code. The logging unit suite was rerun after that adjustment.
- Total: **779 distinct passing tests**, one optional module skip. Repeated focused runs are not added to this total.
- Ruff check and format check on the five changed Python files — PASS.
- `uv run ty check app/core/openai/chat_requests.py app/core/runtime_logging.py` — PASS.
- `npx --yes @fission-ai/openspec@1.11.0 validate verify-plan-json-metrics-contracts --strict` — PASS.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict` — **68 passed, 0 failed**.
- `git diff --check` and separate UTF-8/whitespace checks for new artifacts — PASS. An independent comparison against HEAD confirms exactly UP-PR-2512/2515/2529 registry rows changed and all three normative deltas match the main specs.

## Independent contract review

| Dimension | Verified scope |
| --- | --- |
| Completeness | 6/6 tasks, 3/3 selected registry items, 3/3 synchronized requirements |
| Correctness | 10/10 delta scenarios mapped to product and focused regression evidence |
| Coherence | Existing normalization, alias, and shared logging boundaries retained; no critical/warning findings |

Reviewed the final implementation separately from the red/green test run. All three delta requirements map to product evidence above; all six implementation/completion tasks are required before archive. No critical or warning-level mismatch remains.

- Chat format detection runs after mapping response_format to text controls, using the same predicate as Responses normalization; removed helper has no remaining code consumer. Existing JSON-schema/plain-message/Lite/compact and cache-key regressions are in the focused suites.
- JSON access tuple extraction does not mutate shared LogRecord state; explicitly structured records still use their existing fields. Two handlers therefore render the same access event without depending on formatter order. Both 200 and 503 are covered.
- Enrichment skips only diagnostics from the helper's own logger, preventing failed lookups from looking themselves up again. Ordinary trace/span enrichment remains covered by test_otel; missing optional tracing is exercised by actual CLI debug startup.
- Real refresh persistence is read from a separate session. The credential tuple, account ID, and workspace remain unchanged; refusing a payload writes neither metadata nor usage.
- Code graph refreshed for the current checkout. Its integration-test directory is excluded from indexing, so HTTP/subprocess boundaries were verified directly in source and runtime rather than inferred from graph edges.

## Completion and limits

Normative deltas and stable context are synchronized to the three main capabilities. The change is archived only after strict validation and all tasks pass. issues-check.md records the same three local closures and findings F-057/F-058/F-059 with this evidence link.

The initial checkout was clean. No changelog edit, commit, push, deployment, release, cloud workflow dispatch, or public GitHub issue closure is part of this batch. Cloud CI, hosted provider/Codex UI behavior, native helper artifacts, PostgreSQL replicas, POSIX signal shutdown, and public packages/images are not certified by local SQLite/Python/Windows checks.
