# Native client compatibility verification — 2026-10-02

Base HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`. Changes are local and uncommitted, layered on the existing dirty checkout. Selected registry scope: exactly UP-ISSUE-2356, UP-ISSUE-2128, UP-ISSUE-2038.

## Findings and reproduction

- #2356: existing native history/notes routes work. The remaining local evidence gap was operation/alias coverage, opaque body/query/header preservation, scoped authentication, child-thread placement and unavailable upstream behavior. Added coverage; no new runtime defect attributed to this item.
- #2128 / F-046: slash search requests returned 405 on canonical, v1 and duplicated-prefix ingress because the catch-all handled the unmatched path. Hidden slash routes now reuse the control handler directly.
- #2038 / F-047: `/v1/models/gpt-5.2/` and `/v1/models/vendor/model/` returned 404, despite visible matching catalog items. A hidden slash route registered before the greedy route preserves the internal slash and removes only the delimiter.
- Before the runtime patch, the 10-case regression slice produced **5 failed, 5 passed**: three 405 search cases and two 404 model cases. After the patch all cases pass.

## Final checks

| Check | Result |
| --- | --- |
| `uv run --frozen pytest tests/integration/test_native_client_compatibility.py tests/integration/test_proxy_native_history_notes.py tests/integration/test_v1_models.py -q --tb=line --show-capture=no` | **229 passed**, 152.16 s |
| `uv run --frozen pytest tests/integration/test_proxy_api_extended.py tests/unit/test_codex_upstream_paths.py -q --tb=line --show-capture=no -k 'alpha_search or codex_control_request'` | **15 passed**, 163 deselected |
| `uv run --frozen pytest tests/unit/test_client_setup_examples.py tests/unit/test_installation_documentation.py -q --tb=line --show-capture=no` | **16 passed** |
| Ruff check and format check on the five changed Python files | **PASS** |
| `uv run --frozen python scripts/check_proxy_architecture.py` | **PASS** |
| `uv run --frozen python .github/scripts/check_simplicity_budgets.py` | **PASS**, limits unchanged |
| `uv run --frozen --group docs mkdocs build --strict --site-dir <temporary-directory>` | **PASS** |
| OpenSpec 1.11.0 strict change validation | **PASS** |
| OpenSpec 1.11.0 `validate --specs --strict --json` | **68/68 PASS** |
| Exact delta/main-spec comparison | All three added requirement blocks occur exactly once |
| `git diff --check` | **PASS** |

The final runs cover **260 distinct tests**. Earlier baseline/reproduction/retry runs are not added to that total. The only pytest warning is the existing Starlette/AnyIO deprecated BlockingPortal alias.

## Independent contract and transport review

| Dimension | Evidence |
| --- | --- |
| Completeness | Three selected registry entries, three normative delta blocks, five implementation/verification tasks and verified archive preparation |
| Correctness | 96 known-operation variants (60 POST and 36 GET), 18 unknown-operation variants, six child-placement/fallback cases, API-key scope/auth cases, nested model IDs, independent source/allowlist exclusions, unknown models and reservation cleanup |
| Coherence | Three route decorators only; existing auth/control/catalog services reused; no configuration, migration, ownership-policy or transport fallback change |

Second-pass review checked decorator registration order against the greedy model path, scoped catalog logic against list behavior, and each normative sentence against tests. It narrowed the opaque-body promise to POST; GET notes operations forward their query without inventing a body. No unaddressed implementation finding remains. This review was performed within the same chat, without a separate reviewer agent.

Six tests use a real loopback aiohttp upstream with gzip bytes. They pass through the public HTTP route, account selection, real Python control client, header filtering and response adapter: exact body/query preservation, a single media-type field, decompressed nonempty JSON and omitted Content-Encoding/Set-Cookie. Routed control transport regressions independently cover JSON/SDP and three Content-Type spellings.

## Scope limits

Synthetic upstream output and encryption-header values do not prove live ChatGPT search, encryption/decryption, account-pool history recovery or Visual Studio UI registration. No production data, hosted deployment, GitHub issue closure, commit, push, cloud CI, image or package publication was performed. Historical public artifacts are not certified by local source checks.
