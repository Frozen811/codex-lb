# Five open records: local verification

Date: 2026-10-05 (Europe/Kiev). Base: `f987d08e69978ee6452c4e5997b11e80a81ba5f2`.
Selected records: **UP-PR-2548 / UP-PR-2549 / UP-PR-2550 / UP-PR-2558 / UP-PR-2569**. All five were independently read from GitHub and were OPEN, not merged, with heads `7d15ce74ef10`, `1f6c318194d1`, `4febcb53fc4c`, `beee57070eeb`, `9818f7ed4fb1` respectively. Those remote states are source context, not cloud readiness claims.

## Completeness and correctness

| Record | Implementation and evidence | Local result |
|---|---|---|
| UP-PR-2548 | Remove the role-specific resolver and use the existing generic lifetime policy at password/TOTP issuance. Five remote API scenarios validate Max-Age, embedded expiry, reuse without rolling, and rejection after absolute expiry; 3600 / 1224000 / 2592000 apply exactly, 2592001 / 31536000 retain remote 43200. Existing locality, OIDC and TOTP suites pass. | Fixed, locally closed |
| UP-PR-2549 | Existing GET individual-model implementation was freshly exercised by full `test_v1_models.py` and individual-model native compatibility selectors: list-entry equality, nested IDs, client-version handling, canonical/slash, assigned sources, allowlist/auth denial, unknown model envelope and catalog-failure reservation release. Shared visibility and serialization were reread. | Existing implementation verified, locally closed |
| UP-PR-2550 | Existing main Authorization behavior passed, but a fresh malformed Proxy-Authorization parameter-list probe leaked the synthetic credential in WARNING text/JSON (two failing formatter cases). Explicit matcher now covers proxy headers, including single-quoted malformed fields. Complete quoted Python-repr Basic values retain only the scheme and placeholder, never credential tails. 22 fresh formatter scenarios and full structured logging pass. | Fixed, locally closed |
| UP-PR-2558 | Replace tokens/credits division with percentage points per default-size token estimate; runtime pressure stops at 99 below that boundary and retains reported 99/99.5/100 and unknown usage. Persisted fields on transient AccountState drive both zero-score/zero-weight relative-availability fallbacks. Real SQLite selection and sticky readback, three plans, zero weight, proportional 16384-token estimate, seeded fallback and unknown usage pass. Existing leases are released in test finalizers. | Fixed, locally closed |
| UP-PR-2569 | Developer messages remain in input with original content/order; absent instructions defaults to empty, system normalization and JSON mode remain supported. Four actual local HTTP chained-history scenarios, two downstream WebSocket route chains with controlled upstream, compact canonical wire and slash refusal, six model validation/serialization cases, Chat JSON wire and two updated golden records pass. | Fixed, locally closed |

## Red-before evidence

- After removing fixture-only mistakes, remote lifetime selector failed at configured **1224000 / 2592000** (`43200` actual); short and >30-day boundaries passed. The test uses `lb.example`, because `testserver` is intentionally local in repository test infrastructure.
- Ten direct account-state cases demonstrated mixed-unit pressure or false exhaustion across Plus/Pro/unknown-capacity plans. For 38 percent + 10240 tokens, old actuals were 100 / 58.317460317 / 38 rather than 39.
- Two real-DB selection/sticky cases selected `a-heavy` at 95 instead of `z-light` at 38. The initial fixture used an unsupported deterministic keyword; that was corrected before the valid negative control. Canonical sticky keys and legacy key provenance are exercised.
- Six developer normalization cases lost input, and four actual HTTP chain cases returned `missing reference` because only input was inherited by the recording upstream. All ten pass after preserving developer messages.
- Two new WARNING formatter cases exposed `SYNTHETIC_PRIVATE` in malformed Proxy-Authorization. Both pass after the matcher repair; the final 22-case selection also exercises quoted malformed fields and placeholder tails.
- Initial compact fixture endpoint assumptions were corrected to the current `/codex/responses` transport. Existing compact trailing-slash POST is 405; the test asserts no dispatch, preserving that contract.

## Commands and results

All Python commands use `uv run pytest`, isolated test DBs and synthetic data. Commands below are focused selections; counts are **not additive**, since some selections overlap.

| Command / selection | Result |
|---|---|
| `tests/integration/test_five_registry_contracts.py tests/unit/test_openai_requests.py tests/unit/test_dashboard_session_ttl.py -q --tb=short --show-capture=no` before adding compact wire cases | 239 PASS |
| `tests/unit/test_load_balancer.py tests/unit/test_routing_tunables.py tests/integration/test_load_balancer_integration.py -q --tb=short --show-capture=no` before moving the same pressure arithmetic to tunables | 325 PASS; subsequent final new/scoped selections cover the extracted helper |
| `tests/integration/test_v1_models.py tests/unit/test_structured_logging.py -q --tb=short --show-capture=no` | 216 PASS; fresh redaction subsequently found and fixed the separate proxy-header gap |
| `tests/integration/test_plan_json_contracts.py tests/integration/test_proxy_responses.py tests/integration/test_proxy_chat_completions.py tests/integration/test_dashboard_password_auth.py tests/integration/test_dashboard_totp_auth.py tests/integration/test_oidc_login_flow.py tests/integration/test_step_up_auth.py -q --tb=short --show-capture=no` | 268 PASS, 226.98 seconds |
| `tests/integration/test_native_client_compatibility.py tests/unit/test_passthrough_request_fields.py -q --tb=short --show-capture=no -k 'individual_model or forwarded_payload_bytes_match or corpus_covers'` | 23 PASS, 93 deselected; all 12 golden entries checked |
| `tests/integration/test_proxy_compact.py -q --tb=short --show-capture=no` | 57 PASS |
| `tests/unit/test_open_registry_redaction_contracts.py tests/unit/test_structured_logging.py -q --tb=short --show-capture=no` after final matcher repair | 119 PASS |
| `tests/integration/test_five_registry_contracts.py tests/unit/test_lease_pressure_contracts.py tests/unit/test_open_registry_redaction_contracts.py tests/integration/test_proxy_websocket_responses.py -k 'five_registry_contracts or lease_pressure_contracts or open_registry_redaction_contracts or previous_response_chain_keeps_developer_input' -q --tb=short --show-capture=no` | **70 PASS**, 212 unrelated WebSocket cases deselected, 16.14 seconds; no skips/failures |
| `bun run test src/features/settings/components/routing-settings.test.tsx` in frontend | 45 PASS |
| Scoped `uv run ruff check`, `uv run ruff format --check` | PASS; 16 changed Python files |
| `uv run ty check` for the seven changed application files | PASS |
| `scripts/check_proxy_architecture.py`, `scripts/check_cancellation_safety.py`, `scripts/check_proxy_timing_seams.py`, `scripts/check_settings_tiers.py` | PASS; size gates preserved, 98/98 setting fields |
| `uv run python .github/scripts/check_simplicity_budgets.py` | PASS; no new setting/nav/README/root budget usage |
| `npx.cmd --yes @fission-ai/openspec@1.11.0 validate repair-five-auth-routing-input-contracts --strict` | PASS |
| `npx.cmd --yes @fission-ai/openspec@1.11.0 validate --specs --strict` | 68/68 PASS |
| Requirement comparison after sync | Six delta/main requirement blocks equal; stable context synchronized in four capabilities |
| `git diff --check` | PASS |

## Coherence and independent reread

The source graph located request normalization, password issuance, scoring and model serialization; current source and runtime evidence were authoritative. Final source was reread against six normative blocks. Selection keeps eligibility, caps and ownership outside the new arithmetic; no I/O is added under the runtime lock. The relative fallback only changes its own two zero-weight branches and preserves seeded ties and other strategy behavior. No schema, migration, configuration surface or dependency change was introduced.

The lease reference is correctly described as **default size**, not maximum. Current input/output estimates can each cap at 8192; 16384 therefore gives 1.6 points at weight 1. This is tested rather than copying the upstream PR's inaccurate maximum description. Dashboard help was updated in English, Korean and Chinese, and owning OpenSpec/context plus existing routing docs agree.

Existing Basic Python-repr rendering remains pinned. The proxy authorization matcher treats placeholders as untrusted for unquoted tails and masks quoted Basic tails fully; text and JSON WARNING paths, subsequent line preservation and idempotence are tested.

## Unrelated baseline failure and external limits

Broader `test_passthrough_request_fields.py` found **nine failures** in `test_passthrough_nesting_at_the_limit_is_accepted_and_serializable`, with Pydantic `Circular reference detected (depth exceeded)`. A separate Python process loaded the exact `HEAD:app/core/openai/requests.py` via an import hook from a disposable temporary file, without replacing working-tree files. The same selector reproduced **9 failed / 3 passed / 73 deselected** on baseline. F-082 remains open; depth-limit serialization is not claimed repaired. Golden payload assertions all pass. This broader module is not aggregate-green.

An ancillary logging-loop module skipped because uvloop is unavailable on this Windows host (130 other cases passed in that exploratory selection). Windows testing does not establish POSIX uvloop runtime behavior. A Starlette/AnyIO deprecation warning is present in Python tests.

Actual HTTP forwarding uses a recording loopback upstream. The WebSocket chain uses the real downstream route with a controlled upstream adapter. Hosted provider persistence/cache, reconnect replay, distributed databases/races, installed client UI, new cloud CI, published artifacts and production are not established by these results. Existing F-045/CI-04 and other partial/public/cloud residuals retain their status. No commit, push, merge, release or deployment is performed.

## Registry preservation and archive

Before closure, all **338** source rows matched the saved pre-edit snapshot, including the user's preexisting 41-record queue refresh. Exactly the five selected source rows receive local closure and this evidence link. Related issues #2554/#2563 and other source rows are inspected for scope but not automatically closed as additional selected tasks. Final saved-row readback, source-row preservation, archive status and the final focused run are recorded below after completion.


## Final current-code receipt

`uv run pytest tests/unit/test_openai_requests.py tests/unit/test_load_balancer.py tests/unit/test_routing_tunables.py tests/unit/test_dashboard_session_ttl.py tests/unit/test_lease_pressure_contracts.py tests/unit/test_open_registry_redaction_contracts.py tests/unit/test_structured_logging.py tests/integration/test_five_registry_contracts.py -q --tb=short --show-capture=no`: **684 passed, no skips/failures, 25.34 seconds**. This run followed the final pressure extraction, proxy redaction and compact fixture correction. The separate 70-case selection includes the two downstream WebSocket chains. Final scoped Ruff/format (16 files), ty (7 app files), architecture/cancellation/timing/settings/simplicity and whitespace checks PASS.

The saved registry was reread: exactly the five selected source rows changed; 333 others equal the pre-edit snapshot; all selected statuses explicitly locally closed with the archive evidence link. Status-field counts are 65 locally closed / 7 partial / 266 pending, total338. F-078–081 are locally closed; F-082 is confirmed/open. Preexisting source refresh and historical evidence remain intact. No sixth source task was selected or closed.


Archive receipt: `npx.cmd --yes @fission-ai/openspec@1.11.0 archive repair-five-auth-routing-input-contracts --yes --skip-specs` reported Task status Complete and created `2026-10-05-repair-five-auth-routing-input-contracts`. Spec writes were skipped because the six blocks had already been manually synchronized and strictly validated. After archive, 9/9 task checks, all six delta/main comparisons, all 20 runtime/test SHA-256 fingerprints, all selected saved statuses, archive evidence links and 333 preserved source rows were checked again and passed.
