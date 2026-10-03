# Verification: verify-planner-scim-cache-admission

Date: 2026-10-02. Base HEAD: `f52adb7274c96c0702e19aa02eabd4f1c7556231`.
Exactly three registry tasks: UP-PR-2540, UP-PR-2541, UP-PR-2545. Existing
dirty changes were preserved. No commit, push, release, or deployment.

## Summary

| Dimension | Evidence |
|---|---|
| Completeness | Three tasks verified; two additional reproduced defects fixed; eight implementation/checklist tasks complete at final audit |
| Correctness | Two modified requirement blocks and all eight delta scenarios map to tests below; existing cache contract independently checked |
| Coherence | Strict clock admission retained; no data migration or implicit repair; SCIM shares one bounded reader; cache pending ownership unchanged |

## Red before / green after

Before production edits, new planner/SCIM route cases gave **13 failed,
4 passed**. Four malformed legacy clock variants crashed response validation;
`99:99` was already readable. Six declared-length refusals failed (including
integer conversion errors for long decimal strings and superscript two, and
body consumption for other malformed lengths). Three valid zero-padded
exact-limit writes also hit the integer conversion limit.

After fixes, all **26 selected new/expanded route cases passed**. The initial
cache probe had a test-only wrong helper keyword; it was corrected to install
the independent peer routing cache in the existing global cache seam. It
does not establish a production cache defect. No cache runtime edit was needed.

## Requirement and scenario mapping

| Scenario / existing contract | Executable evidence |
|---|---|
| Impossible ASCII clock time / atomic refusal | `test_quota_planner_rejects_invalid_clock_time_without_saving`, both fields, impossible ranges, Unicode and trailing newline; strict unit validation remains |
| Clock boundaries / omitted and null fields | `test_quota_planner_clock_time_boundaries_and_partial_updates` |
| Malformed historical clocks remain visible and correctable | `test_legacy_clock_times_remain_readable_and_individually_correctable`: five strings, GET settings, GET forecast, empty/null updates, start-only then end-only correction, real saved values |
| Stream without declared length / false declared length | `test_an_oversized_stream_stops_at_the_scim_body_limit`: POST/PUT/PATCH × absent/understated length, stop after crossing chunk, unchanged resource and one identity in DB |
| Valid fragmented body, including exact limit and leading zeroes | `test_scim_valid_resource_at_exact_stream_limit`: three methods × normal/5000-leading-zero header, resource readback |
| Oversized/malformed declared length safely refused | `test_scim_declared_length_is_refused_without_reading_or_writing`: huge decimal, zero-padded huge, negative, nondecimal, empty, non-ASCII digit; SCIM 400/413, no receive, no identity |
| Original ordinary declared-length precheck | `test_an_oversized_body_is_refused_before_it_is_read` |
| Failed immediate publication after committed mutation | `test_failed_pause_publication_retries_and_refreshes_peer_routing`: locked DB, driver exception, cancellation through real Pause route; actual PAUSED row and local routing, pending marker, real version retry, separate peer routing snapshot, stale ACTIVE bridge reuse refusal |
| Cancellation/backoff/ambiguous commit/new pending marker | `tests/unit/test_cache_invalidation_poller.py`, existing tests kept |
| Namespace isolation and running poller recovery | `tests/integration/test_cache_invalidation_bus.py`, existing failure/flush/background tests kept |

## Final targeted run

```powershell
uv run pytest tests/unit/test_quota_planner.py tests/integration/test_quota_planner_api.py tests/unit/test_scim_body_limit.py tests/integration/test_scim_v2_users.py tests/unit/test_cache_invalidation_poller.py tests/integration/test_cache_invalidation_bus.py tests/unit/test_request_body_limit_middleware.py -q --tb=line --show-capture=no
```

**225 passed, 1 skipped** in 110.78 seconds. The existing non-UTC `tzset`
test skips on Windows. One existing Starlette deprecation warning. Baseline
and selected reruns are not added to this final total.

Additional checks: Ruff check and format on all five changed Python files;
targeted `ty check` on the two production files; proxy architecture,
cancellation safety, timing seam and simplicity budget scripts; strict
OpenSpec 1.11.0 change validation and all **68 main specs** — PASS.

## Second review

A second source/scenario pass verified the current implementation against
each delta scenario and the existing cache contract, rather than accepting
the ISSUES.md author counts. No separate reviewer agent was used.

- Read clock schema and consumer: update pattern remains ASCII/range strict;
  response is a string contract already accepted by the frontend Zod schema.
  Null/omitted updates preserve current values; forecast fallback leaves DB
  values unchanged. No frontend rendering edit was made.
- Read SCIM reader and global ingress: syntax checks do not convert long
  decimal strings; zero stripping preserves magnitude; lexicographic comparison
  is only used at equal digit count; actual chunk budget is checked before
  extending the buffer. Refusal occurs before resource writes.
- Read poller and route consumers: unsuccessful bumps restore markers in
  synchronous finally, cancellation propagates, successful completion does
  not erase markers enqueued during a write, namespaces remain isolated.
  The real retry uses its own session, and peer snapshot callbacks own their
  sessions. No concurrent task shares one AsyncSession.
- Delta/main requirement blocks were synchronized exactly. No outstanding
  critical issue or uncovered delta scenario remains in this local scope.

## Limits

SCIM malformed-header guarantees apply when a request reaches ASGI; h11,
nginx, or other servers may reject malformed framing earlier. No live identity
provider was used. Cache retry queue is in memory and does not guarantee
delivery after source-process loss; existing TTL/reconcile backstops remain.
Public artifacts, deployed replica infrastructure, MySQL/PostgreSQL runtime,
cloud CI, and the unrelated Windows `tzset` scenario were not certified by
this batch. Exactly these three registry rows are locally closed.
