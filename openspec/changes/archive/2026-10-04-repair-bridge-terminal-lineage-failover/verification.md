# Verification: bridge continuation contracts

Date: 2026-10-04 (Europe/Kiev). Base HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`.
Scope: exactly UP-ISSUE-2493, UP-ISSUE-2465 and UP-ISSUE-2455 from issues-check.md.
Changes are local and uncommitted. No push, release, deployment or cloud gate is claimed.

## Findings and corrections

The existing runtime paths implement the checked contracts. This batch adds real-origin/API-key/SQLite route evidence, repairs the unsafe full-resend unit fixture (F-067), corrects the three historical ISSUES.md descriptions and closes their own registry rows. No app/ or Rust implementation was changed by this batch.

F-067 reproduced as 6 failed / 101 passed in the bridge unit selection and 6 failed / 4 passed in an isolated rerun. The partial durable mock left owner retirement pointed at SQLite without an accounts table. Its non-retiring double now asserts the expected account and preserves every original unsafe-input refusal assertion. The same selected 107 cases pass.

The real-origin fixture uses generous token limits so an independent admission budget does not stop an anchor test. Completed usage is explicit; the first warm response finalizes its reservation with input/output=1/1. Subsequent denial/recovery checks require all reservations to be released or finalized. Multiple reservations can arise during existing late-anchor reconciliation, so the tests assert settlement rather than assuming one row per logical request.

The eventless route test sends two distinct silent logical turns, then retries the last complete body after poison settlement. Each turn has a bounded send count and deadline; the successful retry contains the full input and no poisoned anchor. An identical recovery checkpoint before poison settlement can hit the existing active-claim refusal. That guard is preserved; silence alone does not authorize duplicate operation dispatch. Existing consecutive-strike and operation-journal tests supplement the real-origin sequence.

## Completeness, correctness and coherence

| Dimension | Assessment |
|---|---|
| Completeness | Three source rows handled; six change tasks complete; one requirement with six scenarios synchronized |
| Correctness | Native pre/post-commit outcomes, denied-anchor retirement, scoped quota proof, owner negatives, fresh lineage and image/tool Lite payloads mapped to passing route/unit evidence |
| Coherence | Existing session/account/reservation/task owners and replay guards retained; test retirement remains non-retiring; no new setting, schema, dependency or nav surface |

No unresolved critical or local warning finding blocks this verified local scope. External certification is explicitly excluded below.

## Runtime evidence

Counts belong to each command. These are focused verification commands, not a full-suite or CI aggregate result.

| Command | Result |
|---|---|
| `uv run pytest -q tests/integration/test_bridge_continuation_contracts.py --show-capture=no --tb=short` | 27 passed |
| `uv run pytest -q tests/unit/test_proxy_http_bridge.py -k 'denied_bridge_anchor or denied_anchor or poison or full_resend or keepalive_counts_as_first_yield or anchor_rejection_after_keepalive' --show-capture=no --tb=short` | 107 passed; 976 deselected |
| `uv run pytest -q tests/integration/test_http_responses_bridge.py -k 'denied_anchor or replays_verified_full_resend_after_stale_owner or quarantines_reattach or quarantined_unsafe_full_resend' tests/integration/test_responses_lite_parallel_tools.py tests/integration/test_http_bridge_multiline_json.py --show-capture=no --tb=short` | 28 passed; 226 deselected; the filter applies to every supplied file |
| `uv run pytest -q tests/integration/test_responses_lite_parallel_tools.py tests/integration/test_http_bridge_multiline_json.py tests/unit/test_http_bridge_eventless_semantics.py tests/unit/test_http_bridge_cancel_drain.py tests/integration/test_http_responses_bridge.py::test_v1_responses_http_bridge_stops_reinjecting_an_anchor_upstream_denied --show-capture=no --tb=short` | 98 passed; covers those entire small suites without the preceding filter |
| `uv run pytest -q tests/integration/test_proxy_transient_retry.py tests/integration/test_proxy_responses.py -k 'http_bypass_quota_failover_requires_verified_full_history or legacy_raw_owner_conflict' --show-capture=no --tb=short` | 8 passed; 220 deselected |

The new cases comprise four native canonical/slash pre/post-commit denial cases, eight v1/backend image/tool Lite HTTP cases, fourteen scoped canonical/slash payload-fallback cases and one repeated-eventless/fresh-retry sequence. Upstream socket traffic is real local WebSocket/HTTP; service/repository/reservation paths use the application and isolated SQLite. Owner mismatch is an injected conflicting lookup/resolver control; vendor traffic is not involved.

## Static and specification checks

- `uv run ruff check tests/integration/test_bridge_continuation_contracts.py tests/unit/test_proxy_http_bridge.py`: PASS.
- `uv run ruff format --check tests/integration/test_bridge_continuation_contracts.py tests/unit/test_proxy_http_bridge.py`: PASS, two files formatted.
- `uv run ty check tests/integration/test_bridge_continuation_contracts.py tests/unit/test_proxy_http_bridge.py`: PASS.
- `uv run python scripts/check_proxy_architecture.py`: PASS.
- `uv run python scripts/check_cancellation_safety.py`: PASS.
- `uv run python scripts/check_proxy_timing_seams.py`: PASS.
- `uv run python scripts/check_settings_tiers.py`: PASS, 98/98 settings.
- `uv run python .github/scripts/check_simplicity_budgets.py`: PASS, unchanged budgets.
- `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict --no-interactive`: PASS, 68/68 main specs.
- Strict validation of this change: PASS. Delta requirements equal the synchronized main requirement block.
- `git diff --check`: PASS.

## Preservation and boundaries

The initial snapshot contained 76 dirty/untracked files. Every preexisting file outside ISSUES.md, issues-check.md and the owning responses-api-compat spec/context remains byte-identical. Previous spec/context content is preserved as a prefix; other source-queue rows and the historical sections remain unchanged. The unit fixture file was initially clean and has a focused eight-line change.

All three own registry rows and the latest summary are locally closed and linked here. The change is archived only after verification. This does not certify new GitHub CI, public packages, real Factory/Codex/macOS traffic, provider overload/cache percentages or production. F-045/CI-04 and other public/platform residuals remain open.

## Source fingerprints

SHA-256 values identify the exact local source and test snapshot used for these results.

| Path | SHA-256 |
|---|---|
| `app/modules/proxy/_service/http_bridge/streaming.py` | `0508135a8a873cfd475243312d8bc5a1b34a77cb410ab0d39f59ab4fb9dd9bfd` |
| `app/modules/proxy/_service/http_bridge/upstream_events.py` | `3182d0a837905ba0de3b53cfa37a4b9419ad830e66f50cbf4a2f1c06e48872b6` |
| `app/modules/proxy/_service/http_bridge/retry_circuit.py` | `4d6dd344cbf19d7464a98045d2c79be78e57d6a95abc3efde6cc640f8f667227` |
| `app/modules/proxy/_service/http_bridge/request_submit.py` | `db728717558cb463d048396db689f0dddedc5e7a246263e07a53d0cebd141fb3` |
| `app/modules/proxy/_service/streaming/retry.py` | `32537ec48e6b717a65eb45c3d4184a2ae9c2d02cbc8f02b5aaac88469ed55f2e` |
| `app/modules/proxy/api.py` | `c945e89f40810fa5969ed84f99d51f11a615c9736f80917fbcc216677872cf0e` |
| `app/core/clients/proxy.py` | `d823bdca331246f8ec0a3339e1fe6e08143c3ae279c3265e838eaa986ba6d9a5` |
| `app/core/clients/proxy_websocket.py` | `f14ec9b9b212b70ad0a426930c7379c498f21e6ba258997cbedaa0ff4569d4c9` |
| `tests/integration/test_bridge_continuation_contracts.py` | `64a6b2edca4d1117a10c7dccb331bb8d73098f646580600802ba422b020b96e3` |
| `tests/unit/test_proxy_http_bridge.py` | `4d909927ffe51e96057056133c4a7ff5dee634edc52644a7177828f5c4b5d518` |
