# Verification: quota warmup fallback and reset cycles

Date: 2026-10-05, Europe/Kiev. Clean starting source: `a8e892c66d1476e90afdde4b762c38f1d0dd5864`. Branch: `codex/repair-warmup-three`. Exactly three selected registry rows: UP-ISSUE-1895, UP-ISSUE-1976, UP-ISSUE-1975. Evidence is local source/HTTP/SQLite; no GitHub CI, push, package, or deployment claim is made.

## Findings and resolution

- **1895 / F-076:** the existing compact-404 fallback and Force Probe work on the real HTTP path and omit unsupported fields on the wire. The producer still supplied max_output_tokens, but the common transport already filtered it, so this alone was not a confirmed wire failure. Two real route cases confirmed that a completed response with no usage manufactured `(1, 1)` input/output token counts in the persisted request log. The fallback now preserves absent usage, requires completion even if an adapter silently exhausts, explicitly closes its iterator, and omits the unsupported producer field. Selected-account identity, one fallback, non-404 refusal, usage 5/3, error/incomplete/EOF handling, and released stream capacity are verified.
- **1976 / F-077:** six SQLite service cases confirmed a second send in the same stable cycle after a sliding deadline moved 121 seconds, beyond timestamp jitter tolerance. Claims now use the cycle end used for slot scheduling. Non-zero slots retain the existing sliding-horizon heuristic. Slot zero only uses the stable phase when consecutive usage snapshots prove matching deadline/observation-clock movement. This avoids the fixed-window regression found by `test_staggered_idle_slot_uses_observed_window_duration`. All three indices, 180/300-minute durations, moving/fixed deadlines, reopened DB sessions, zero cooldown, and the next cycle are covered.
- **1975:** no further production defect was found. Existing durable reset-history recovery passes 29 real live-ingestion/scheduler/SQLite tests, including fresh polling skips, restart, duplicate workers, 240 later snapshots, pending/succeeded/failed/skipped claims, later real polls, expired/superseded/insufficient quota, opt-out, incomplete history, and late delayed-deadline recovery. The existing requirement remains authoritative; neither a journal-only closure nor a helper-only pass is used.

## Executed verification

| Command | Result |
|---|---|
| `uv run pytest -q tests/integration/test_warmup_contract_wire.py -k 'no_usage or cycle_claim' --tb=short --show-capture=no` before production fixes, after fixture repairs | **8 failed, 6 passed**, 13 deselected; 7.03 s. Two fake token-count failures and six duplicate-send failures. |
| `uv run pytest -q tests/integration/test_live_reset_warmup.py --tb=short --show-capture=no` | **29 passed**, 20.67 s; existing behavior independently confirmed. |
| Initial combined six-module selection after first production fixes | **206 passed, 1 failed**, 101.99 s; fixed-window phase regression discovered and repaired. |
| `uv run pytest -q tests/unit/test_limit_warmup.py tests/integration/test_warmup_contract_wire.py --tb=short --show-capture=no` after phase refinement, before three adapter controls | **101 passed**, 15.84 s. |
| `uv run pytest -q tests/integration/test_warmup_contract_wire.py tests/integration/test_live_reset_warmup.py tests/integration/test_proxy_warmup.py tests/integration/test_accounts_api_probe.py tests/unit/test_limit_warmup.py tests/unit/test_accounts_service_probe.py --tb=short --show-capture=no` final selection | **210 passed**, 83.05 s; no failures or skips. Includes 30 new controls: 14 real HTTP fallback outcomes, one Force Probe wire case, 12 SQLite cycle cases, three route/adapter controls. |
| `uv run ruff check .`; `uv run ruff format --check .`; `uv run ty check --output-format concise` | PASS; 1459 formatted files, no type diagnostics. |
| `uv run python scripts/check_proxy_architecture.py`; `uv run python scripts/check_cancellation_safety.py`; `uv run python scripts/check_proxy_timing_seams.py` | PASS; existing ratchets remain intact. |
| `uv run python .github/scripts/check_simplicity_budgets.py` | PASS; root 0/0, nav 5/5, no new setting or README section. |
| `npx.cmd --yes @fission-ai/openspec@1.11.0 validate --specs --strict` | **68 passed, 0 failed**. |
| `npx.cmd --yes @fission-ai/openspec@1.11.0 validate repair-warmup-fallback-and-reset-evidence --strict` | PASS; main requirements synced before archive. |
| `git diff --check` | PASS. |

The first wire fixture incorrectly treated only a `/compact` URL as compact traffic; the real transport sends a compaction_trigger on the Responses endpoint. That fixture and two nonexistent pressure-method assertions were corrected before collecting the eight production red-before cases. Those fixture failures are not production findings. The warning in pytest is Starlette's deprecated BlockingPortal alias. Counts above overlap and are not summed as distinct tests.

## Completeness, correctness, and coherence

The proposal's two capabilities each have a tested delta and a synchronized main requirement. Existing persisted-reset behavior is covered without adding a redundant requirement. Code discovery mapped the slot helper, warmup submission, reset recovery and scheduler callers; current source was read before edits. A final diff review confirmed selected-account ownership, cleanup in the existing finally block, fixed-window compatibility, no schema/configuration expansion, and no changes to usage-history recovery.

All eight implementation/verification tasks are complete before archival. Each of the three registry rows and the current summary is updated with this evidence and reread before committing. F-076 and F-077 describe the two confirmed defects; other source-queue rows are not closed by subsystem inference. The local commit containing this artifact is the repair source, identifiable with `git log --all --follow -- app/modules/limit_warmup/service.py` and the corresponding warmup file history.

## Limits

HTTP tests use a loopback recording upstream and SQLite tests use isolated test databases. Slot-zero sliding classification requires matching consecutive observations; initial isolated samples retain the existing fixed-window phase. An old moving-deadline idle claim may differ from the first stable claim after upgrade, bounded by the existing cooldown. No live-provider timing, macOS/ARM64 execution, PostgreSQL/MySQL warmup claims, distributed failover, global RSS, release artifacts, exact-new-head cloud CI, or production deployment is certified. Prior F-045/CI-04 and other explicit external residuals retain their status.
