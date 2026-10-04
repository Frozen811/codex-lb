# Verification: bridge retry and claim lifecycle

Date: 2026-10-04 (Europe/Kiev). Base HEAD: `282ce147038ac53b72bca30d69c4ad9a9ac1b7cc`. Exactly three source rows: UP-ISSUE-2273, UP-ISSUE-2272, UP-ISSUE-2271. Local working tree only; no fixing commit or publication.

## Results by selected row

| Row | Result | Evidence and remaining scope |
|---|---|---|
| UP-ISSUE-2273 | Verified / locally closed | Existing accounting confirmed with raw/interpreted terminals, explicit-error precedence, unknown/missing reasons, eligibility exclusions, real SQLite and loopback HTTP/WebSocket. Separate attempts persist counts 1 then 2; stored-operation replay adds no dispatch or strike. Public v1/slash/backend routes retain authored incomplete payload on the original dispatch. Existing proof-gated recovery is preserved. |
| UP-ISSUE-2272 | Verified / locally closed | Real persisted missing/zero/negative/elapsed values allow repeated admission. A previously observed local cooldown expires into one local probe; repeated loads preserve it. Existing submission/ownership/settlement regressions pass. Deadline expiry alone is not certified as an abandonment policy. |
| UP-ISSUE-2271 | Locally repaired / partially verified | Lost cancellation receipt, missing inserted-row epoch, post-commit receipt replacement and unfenced local probe clearing repaired. Crash reclamation, uncertain internal DB timeout, generation rollback ABA and ordinary-success/newer-claim settlement policy remain open. PostgreSQL/MySQL and migration compatibility execution are not certified. |

## Reproduced defects

- Before the cleanup patch, all three release outcomes (success, CAS rejection, DB exception) set a newer local probe to zero: 3 regression failures.
- After correcting the fixture to reach actual submission and a real coordinator commit, caller cancellation left durable generation 1 instead of releasing to 0: one focused red-before case.
- After caller-cancellation deferral was repaired, the newly inserted-row cancellation case still left generation 1 because the original capture had no epoch: one further red-before case.
- Receipt replacement is checked with a real successor claim performed immediately after commit. The returned receipt stays at generation 1, stored state advances to 2 and old cleanup cannot release generation 2.

Fixture setup errors and provisional over-broad assertions during test development are not counted as reproduced source defects. The loopback fixture closes bridge sessions before stopping its origin; an interrupted exploratory run preceded that correction and is not green evidence.

## Commands and results

Final combined regression run:

```powershell
uv run pytest -q tests/unit/test_bridge_retry_claim_lifecycle.py tests/integration/test_bridge_retry_terminal_contracts.py tests/unit/test_durable_bridge_sessions.py --timeout=20 --tb=short
```

**111 passed** (43 new: 40 unit + 3 real route cases; 68 existing coordinator tests), no skips/failures. This run covers the final source, including local-only captures with no persisted epoch and propagation of deferred cancellation after remaining submission cleanup. One existing Starlette deprecation warning.

Existing subsystem regression run:

```powershell
uv run pytest -q tests/unit/test_proxy_http_bridge.py tests/unit/test_durable_bridge_sessions.py -k 'retry_circuit or half_open or claimed_probe or pre_dispatch_exit or ambiguous_send or elapsed_persisted or claimed_durable or claim_miss or probe_reclaimed or merged_cooldown or anchored_replay_does_not_bypass or lost_claim or claimed_replay' --timeout=20 --tb=short
```

**71 passed**, 1080 deselected. Counts overlap with coordinator coverage and are not added into a full-suite claim.

Final scoped Ruff check/format and `ty check` pass for the three changed app files; Ruff also covers both new test files. Proxy architecture, cancellation safety, timing seams, settings tiers and `.github/scripts/check_simplicity_budgets.py` pass. Strict OpenSpec 1.11.0 change validation and **68/68** main specs pass. No full-repository suite or cloud gates were run.

## Requirement/scenario mapping and second review

| Requirement/scenario | Implementation and executable evidence |
|---|---|
| Incomplete reason, precedence and exclusions | Existing upstream_events terminal path; 24 raw/interpreted cases in `test_incomplete_accounting_raw_and_interpreted_with_real_persistence`, plus three loopback route cases. Deferred reasoning, soft affinity, disarmed send, prewarm, skipped logs, ordinary observed output and safe replay stay excluded. |
| Repeated elapsed/missing cooldown | Existing retry_circuit loader/gate; four real-durable admission cases. |
| Actual local expiry/probe reload | `test_real_cooldown_expiry_admits_one_local_probe_and_preserves_it_on_reload`; existing half-open and predelivery ownership tests. |
| Cancellation after commit / newly inserted receipt | Real submission and SQLite coordinator, six existing/missing/local-only capture and repeated-release-cancellation cases. No send, no pending request, original failure count retained, owned claim released. |
| Local key-lock timeout bound | `test_cancelled_claim_cannot_wait_forever_on_local_key_lock`; owned acquisition ends at its configured bound without sending or changing the durable circuit. |
| Replacement local lease | Three durable-release outcomes retain the replacement lease, cooldown and generation. Exact local lease release remains owned by submission's existing fence. |
| Transaction receipt / successor fence | `test_claim_receipt_cannot_be_replaced_by_a_successor_after_commit`; repository reads the immutable snapshot before commit and performs no post-commit receipt query. |
| Ambiguous dispatch | Existing attempted-send guard and `test_an_ambiguous_send_keeps_the_claimed_probe`; cancellation/claim targeted regressions pass. |

A second manual review followed the passing tests: checked actual CAS predicates, claim task ownership and whole-call bound, exact lease cleanup, deferred cancellation ordering, immutable receipt construction, schema/settings neutrality, public route framing and delta/main equality. No subagent review is claimed. The original durable generation rollback is intentionally unchanged and remains a partial issue boundary, not silently accepted as safe.

## Preservation and boundaries

The initial 97 dirty/untracked files were fingerprinted outside the repository. Only issues-check.md and the owning responses spec/context are intended overlaps; the other 94 original paths must remain byte-identical. The spec/context preserve original bytes as prefixes. Exactly three original source-queue rows receive new statuses/evidence. The archive's fingerprints file records affected source/test hashes and the final preservation check.

Live provider/client, public artifacts, exact-head cloud CI/review, production and pre-existing F-045/CI-04 remain separate. UP-ISSUE-2271 is not fully closed: owner death and abandonment require an accepted policy and supported-database execution; a displayed remote retry bound is not proof of reclaimability.
