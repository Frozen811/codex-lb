# Verification: five retry cleanup contracts

Date: 2026-10-09, Europe/Kiev. Base local main: `005c8aa4d06be1d0d2f1ccdb2e0f90b725884f8e`.
Exactly five initial `НЕ ПРОВЕРЕНО` source rows: UP-PR-2280 / 2276 / 1962 / 2345 / 2278. [Source snapshot](source-snapshot.json) records initial rows, current upstream metadata/patches, 113 prior dirty-file hashes and the external baseline backup path.

## Result by selected entry

| Entry | Current local result | Evidence |
| --- | --- | --- |
| UP-PR-2280 | Fixed missing null-safe `last_detail` deletion fence; existing keyset scan preserves changed rows for the whole pass while deleting independent stale rows. | New database suite: 20 PASS; existing scheduled purge/retention selection: 4 PASS. HEAD reproduction: 8 FAIL and 6 unchanged controls PASS. |
| UP-PR-2276 | Existing service-lifetime quarantine generations and session-identity cleanup independently verified; no additional implementation defect reproduced. | Replacement-owner route matrix includes detached/registered successors with poison, first-strike and weaker evidence; unit generation and completion controls. |
| UP-PR-1962 | Existing exclusive half-open admission/return, cancellation/ownership cleanup and replacement-probe protection independently verified. Missing, zero, negative and elapsed durable cooldown boundaries have new deterministic coverage. | Four new sentinel cases; 40 claim lifecycle cases; focused probe/circuit selection and actual cleanup controls in the unit run. |
| UP-PR-2345 | Existing local failure authority/deadline separation and durable/replay-origin cleanup independently verified. | 54 provenance, 13 provenance-race, 2 recovery-origin and 12 promotion route cases; unit quarantine controls. |
| UP-PR-2278 | Existing reason-only incomplete accounting independently verified with added raw/native-interpreted error/eligibility matrix. | 22 new terminal matrix cases and 6 real HTTP route cases prove durable strike counts, duplicate suppression, unchanged terminal payload, neutral account health and settled API-key reservations. |

UP-PR-1962 and UP-PR-2276 have unresolved upstream acceptance/policy notes. This batch closes the fork's tested local contracts. It does not decide global poison overflow bounds, deadline-only probe reclamation or upstream PR acceptance, nor certify broader live multi-replica semantics.

## Implementation and scenario mapping

The sole runtime edit adds `last_detail` to the existing SELECT snapshot, tuple unpacking and DELETE fence in `DurableBridgeRepository.purge_retry_circuits_before`: three added lines, no schema/configuration change. SQLAlchemy produces `IS NULL` for a NULL snapshot and equality otherwise. [Actual dialect compilation](sql-dialects.json) records 12 SQLite/PostgreSQL/MySQL compilations of the executed DELETE, using NULL and non-NULL snapshots; the execution itself used isolated SQLite.

The complete modified `Retry Circuit Scheduled Purge Fencing` requirement is synchronized to the main spec, retaining both original scenarios and adding detail-only/nullable scenarios. The new database suite covers detail changes in both NULL directions, two non-NULL rewrites, unchanged NULL/string controls, batch sizes 1 and 2, and timestamp/generation/count changes that preserve detail. The count case models a lagging-clock failure. Stable rationale and an example were added to the main context.

Graph navigation established the scheduler caller and existing lifecycle tests before edits. SQLAlchemy's dynamic calls and framework routing were inspected in source and exercised in runtime tests; generic graph edges were not treated as precise call evidence. Existing retry, quarantine, request-submit, upstream-events and support implementations were inspected and left unchanged.

## Exact final checks

All final commands below exited 0. JUnit files retain exact selected test identities and outcomes.

```powershell
uv run pytest tests/integration/test_retry_cleanup_batch.py tests/unit/test_bridge_ring_lifecycle.py -k 'scheduled_cleanup or scheduled_purge or tombstone_outlives' -q --tb=short --junitxml=openspec/changes/repair-five-retry-cleanup-contracts/purge.xml
# 24 PASS, 82 deselected

uv run pytest tests/integration/test_http_promotion_quarantine.py tests/integration/test_http_quarantine_provenance.py tests/integration/test_http_quarantine_provenance_races.py tests/integration/test_http_quarantine_recovery_origin.py tests/unit/test_bridge_retry_claim_lifecycle.py tests/integration/test_bridge_retry_terminal_contracts.py -q --tb=short --junitxml=openspec/changes/repair-five-retry-cleanup-contracts/bridge-routes.xml
# 127 PASS

uv run pytest tests/unit/test_proxy_http_bridge.py -k 'quarantine or half_open or claimed_probe or probe_reclaimed or incomplete_strikes or prelude_is_not_a_pre_response_strike or elapsed_persisted_cooldown' -q --tb=short --junitxml=openspec/changes/repair-five-retry-cleanup-contracts/bridge-unit.xml
# 64 PASS, 1021 deselected

uv run pytest tests/unit/test_proxy_http_bridge.py -k 'retry_circuit or claimed_probe or another_requests_half_open or probe_reclaimed or partial_cleanup_settles or elapsed_persisted_cooldown' -q --tb=short --junitxml=openspec/changes/repair-five-retry-cleanup-contracts/probe-unit.xml
# 50 PASS, 1035 deselected

uv run pytest tests/unit/test_retry_cleanup_contracts.py -q --tb=short --junitxml=openspec/changes/repair-five-retry-cleanup-contracts/incomplete-matrix.xml
# 26 PASS

uv run ruff check app/modules/proxy/durable_bridge_repository.py tests/integration/test_retry_cleanup_batch.py tests/unit/test_retry_cleanup_contracts.py
uv run ruff format --check app/modules/proxy/durable_bridge_repository.py tests/integration/test_retry_cleanup_batch.py tests/unit/test_retry_cleanup_contracts.py
uv run ty check app/modules/proxy/durable_bridge_repository.py tests/integration/test_retry_cleanup_batch.py tests/unit/test_retry_cleanup_contracts.py
uv run python scripts/check_proxy_architecture.py
uv run python scripts/check_cancellation_safety.py
uv run python scripts/check_proxy_timing_seams.py
uv run python scripts/check_settings_tiers.py
uv run python scripts/check_migration_topology.py
uv run python .github/scripts/check_simplicity_budgets.py
npx --yes @fission-ai/openspec@1.11.0 validate repair-five-retry-cleanup-contracts --strict
npx --yes @fission-ai/openspec@1.11.0 validate --specs --strict
# Change valid; 68/68 main specs PASS
git diff --check
```

Final test invocations total 291 passes, with ten shared cases across the two existing bridge unit selections. Deduplicating JUnit `(classname, name)` pairs yields **281 distinct PASS**, **0 skips**, **0 failures**, **0 xfails**. These are focused subsystem checks, not a full repository suite. Warnings are the existing Starlette/AnyIO deprecation; the programmatic HEAD diagnostic also emits PytestAssertRewriteWarning for already imported AnyIO.

## HEAD regression diagnostic

The corrected race injects a committed update immediately before DELETE of the exact selected key. With batch size 1, updating the key after an unrelated earlier SELECT does not model the race; that initial test placement was corrected before the retained diagnostic.

The HEAD method was loaded into the running diagnostic process without changing any worktree file:

```python
import ast, subprocess, pytest
from app.modules.proxy import durable_bridge_repository as module
source = subprocess.check_output(['git', 'show', 'HEAD:app/modules/proxy/durable_bridge_repository.py']).decode()
cls = next(n for n in ast.parse(source).body if isinstance(n, ast.ClassDef) and n.name == 'DurableBridgeRepository')
method = next(n for n in cls.body if isinstance(n, ast.AsyncFunctionDef) and n.name == 'purge_retry_circuits_before')
namespace = vars(module).copy()
exec(compile(ast.Module(body=[method], type_ignores=[]), '<HEAD scheduled purge>', 'exec'), namespace)
module.DurableBridgeRepository.purge_retry_circuits_before = namespace['purge_retry_circuits_before']
raise SystemExit(pytest.main(['tests/integration/test_retry_cleanup_batch.py', '-q', '--tb=short', '--junitxml=openspec/changes/repair-five-retry-cleanup-contracts/purge-head-red.xml']))
```

At execution, before the six metadata control cases were added, this produced **8 FAIL / 6 PASS**, exit 1, stored in [HEAD red evidence](purge-head-red.xml). Every failure was the observed deletion of both rows instead of preservation of the changed one. Current implementation passes all 20 new database cases plus four existing cases. No HEAD source or prior dirty file was temporarily restored/replaced.

## Completeness, correctness and coherence

- Completeness: all five selected local contracts have executed evidence; one modified requirement maps to the three-line implementation and all four scenarios.
- Correctness: red HEAD diagnostic, actual database regressions, route settlement/provenance proof and raw/interpreted exclusion controls pass.
- Coherence: bounded existing scan, SQLAlchemy portability, no new settings/schema/dependencies/dashboard surface; strict main specs and delta validate.
- No actionable local implementation finding remains in the selected scope. [Closure](closure.json) records saved readback of exactly five own rows, 333 byte-identical other source rows, 110 byte-identical unrelated prior dirty files, unchanged prior spec blocks and the complete prior context retained byte-for-byte as a prefix. The shared registry/spec/context edits preserve earlier work. Queue: 338 records, 141 local closures, 7 partial, 190 unverified.

Archive completed with `npx --yes @fission-ai/openspec@1.11.0 archive repair-five-retry-cleanup-contracts --skip-specs --yes --json`, exit 0, at `2026-10-09-repair-five-retry-cleanup-contracts`. Spec updates were skipped by the archive command because the full delta was already merged manually and independently checked for exact equality in closure.json; all eight implementation tasks and planning artifacts were complete before archive.

## Limits

Live PostgreSQL/MySQL, real cross-process/proxy/provider traffic, full-repository testing, public artifacts, cloud CI, releases and production are not certified. Three dialect compilations do not establish live PostgreSQL/MySQL execution. Prior partial findings, F-045/CI-04 and all earlier verification limits remain unchanged. No commit, push, PR, merge, release, deploy or service restart was performed; local HEAD remains the recorded base.
