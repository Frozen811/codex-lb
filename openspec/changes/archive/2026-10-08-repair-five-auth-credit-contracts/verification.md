# Verification: five credential and quota records

Date: 2026-10-08, Europe/Kiev. Base: `8369ec720c5ac935f7a64fe3f30aa1cbc323f5e5`, clean local `main`. Exactly five final selected source rows: **UP-PR-2429, UP-PR-2120, UP-PR-2132, UP-PR-2119, UP-PR-2326**. This report certifies local source/isolated SQLite and synthetic provider execution.

## Current upstream sources

Live GitHub REST bodies, changed paths and exact heads were read before implementation. Upstream state does not imply fork behavior or readiness to merge.

| Record | Current source head | State / interpretation |
|---|---|---|
| [2429](https://github.com/Soju06/codex-lb/pull/2429) | `54887e6d52d8d5479850e836acb36fb6e17fd9f6` | Open; updated title is preserve fixed guardian idle keepalive. Its original shared-eight-day proposal is superseded. |
| [2120](https://github.com/Soju06/codex-lb/pull/2120) | `e4718ddefcce93197ecfb67ae8c9f6c72dac0d32` | Open; ordinary preflight retention is a partial mitigation for refresh credential failure, not a guarantee against daily provider session expiry. |
| [2132](https://github.com/Soju06/codex-lb/pull/2132) | `c9e31b5f01984f64c7dba1d560dc31645524aa06` | Closed; current scope includes rejected-reauthentication stream recovery, credential guards, safe replay and settlement. |
| [2119](https://github.com/Soju06/codex-lb/pull/2119) | `e6626dd1f4e955e32389f35b85744b83f3a3e67e` | Closed; bare credit flag cannot establish spendable secondary capacity. |
| [2326](https://github.com/Soju06/codex-lb/pull/2326) | `77cf311302da72130453192c17b994884291f6c8` | Open; retained reset history supports freshness-skipped polls and existing durable claims. |

Initial candidate issue 2327 was investigated and replaced before coding. Its new schema/distributed operator-probe implementation is excluded; its source row is unchanged.

## Findings and resolution

- **2429 — fixed:** guardian used request `should_refresh`, leaving thirteen-hour-idle active and paused accounts untouched. One UTC-normalized strict twelve-hour predicate now controls admission and fresh-row recheck. Request-time eight-day policy, six-hour cadence, batching, leadership, claims, backoff, cancellation settlement and paused routing status remain intact. The runtime test uses real repositories/AuthManager, synthetic OAuth exchange and persisted token verification; second pass does not refresh again. Existing dashboard copy already describes twelve hours and is unchanged.
- **2119 — fixed:** `credits_has=true` incorrectly admitted an exhausted quota account with missing/zero/negative balance. The shared quota helper now requires positive balance or unlimited credits. Mapper tests cover both windows and primary precedence. Two fresh balancers over real SQLite verify persistent admission/rejection and positive/unlimited controls. Older post-block credit tests now explicitly retain the block for a bare flag. Operator-disabled and clamping tests pass in the broader suite.
- **2120 — fixed deletion race:** ordinary fallback adopted a future-expiry access token even after operator deletion. The latest persisted deletion marker now defeats fallback. Actual `/backend-api/codex/responses` and `/v1/responses` tests prove no dispatch, a failed terminal, unchanged credentials/timestamp/warning and preserved deletion marker. Ordinary visible rows still complete; actual access rejection still fails. Forced-first/ordinary-first shared exchanges and account/session invalidation controls pass. The stable requirement was corrected to exclude session invalidation from the refresh-only whitelist.
- **2132 — existing implementation verified:** auth rejection CAS/rotation and real HTTP transient-retry suites cover same-credential re-encryption, refresh-only rotation, access repair, late cooldown/quota writes, bridge availability, rejected-account exclusion, complete replay, hard ownership, visible-output refusal, leases, deferred settlement and cancellation. No further production edit was required for this record.
- **2326 — existing implementation verified:** the real live ingestion/scheduler suite covers freshness-skipped polls, restart, duplicate workers, retained reset identity, later snapshots/polls, prior claim states, expired/superseded windows and current opt-in/availability. Current scheduler calls `recover_current_reset_evidence`; no redundant recovery ledger or new production edit was added.

## Executed verification

Regression selector:

```text
uv run pytest -q tests/unit/test_auth_guardian.py tests/unit/test_account_mappers.py tests/integration/test_proxy_responses.py tests/integration/test_load_balancer_multi_replica.py tests/integration/test_background_jobs_runtime.py -k 'guardian_idle_age or summary_requires_spendable or preflight_retains or secondary_credit_flag or guardian_runtime_refreshes' --tb=short --show-capture=no
```

Before production edits: **21 failed, 8 passed, 184 deselected**, 12.68 s. After repairs and fixture alignment: **29 passed, 184 deselected**, 11.42 s. The initial guardian refresh stub omitted mandatory result fields; those fixture failures after restoring admission were repaired. Pre-dispatch auth failure uses the existing SSE `response.failed` envelope on HTTP 200, so the deletion test checks the terminal and no-dispatch invariant rather than requiring HTTP 401. Neither fixture correction is an additional production defect.

Final broader command:

```text
uv run pytest -q -n 4 --dist loadfile tests/unit/test_auth_guardian.py tests/unit/test_auth_manager.py tests/unit/test_auth_refresh.py tests/unit/test_account_mappers.py tests/unit/test_load_balancer.py tests/integration/test_auth_preflight.py tests/integration/test_auth_rejection_cas.py tests/integration/test_auth_rejection_rotation.py tests/integration/test_auth_guardian_multi_replica.py tests/integration/test_background_jobs_runtime.py tests/integration/test_load_balancer_multi_replica.py tests/integration/test_live_reset_warmup.py tests/integration/test_proxy_transient_retry.py tests/integration/test_proxy_responses.py --tb=short --show-capture=no --timeout=60 --durations=5
```

**820 passed**, no skips/xfails/failures, 171.56 s. Four workers use the repository's isolated test storage. Four warnings are the existing Starlette BlockingPortal deprecation. The prior sequential broader run had 811 passes and nine outdated expectations/fixture failures and is not claimed green; the final command rechecks the entire selection.

| Additional check | Result |
|---|---|
| `uv run ruff check .` | PASS |
| `uv run ruff format --check .` | PASS, 1483 files |
| `uv run ty check app/core/auth/guardian.py app/core/usage/quota.py app/modules/accounts/auth_manager.py --output-format concise` | PASS |
| `uv run python scripts/check_proxy_architecture.py` | PASS, unchanged ratchets |
| `uv run python scripts/check_cancellation_safety.py` | PASS |
| `uv run python scripts/check_proxy_timing_seams.py` | PASS |
| `uv run python .github/scripts/check_simplicity_budgets.py` | PASS; no new settings/nav/root files |
| `npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict` | 68/68 PASS |
| `npx --yes @fission-ai/openspec@1.11.0 validate repair-five-auth-credit-contracts --strict` | PASS |
| `uv run --frozen --group docs mkdocs build --strict` | PASS, after correcting the owning-spec link to the repository's established GitHub form |
| `git diff --check` | PASS |

The initial `--no-sync` docs attempt had no installed MkDocs. Installing the frozen docs group resolved it without lockfile changes. A relative owning-spec link caused one strict-build warning and was corrected; no documentation validation is bypassed. Test counts overlap and are not summed.

## Completeness, correctness and coherence

Four complete existing requirements, nineteen scenarios and stable context are synchronized. Guardian admission/recheck and ordinary/forced freshness are separately verified. Credit status uses the shared quota helper without changing mapper trust gates or precedence. Deletion authority is checked on the fresh row, with no new concurrent session sharing or task ownership. Existing guarded rejection and reset implementations are exercised instead of duplicated. Documentation explains both refresh policies and links to normative OpenSpec ownership.

All eight tasks are completed before archive. Exactly five source rows receive local closure/evidence; the other **333/333** source rows, including issue 2327, remain byte-identical. Queue remains 338 records: **111 local closures, 7 partial, 220 unverified**. Existing findings, partial records and production residuals are preserved. No critical or actionable warning remains in the verified local scope.

## Limits

No commit, push, PR, merge, new cloud CI, release, provider account, production deployment or live multi-replica PostgreSQL/MySQL execution is certified. Synthetic upstream fixtures verify protocol/service behavior; real SQLite proves local persistence and independent balancer reads. The selected upstream PRs' maintainer/review/cloud gates and the broader historical issue reports remain separate from local fork closure.
