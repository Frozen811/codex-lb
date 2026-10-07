## Decisions and verification

Existing mandatory suites and normal Hypothesis budgets stay in place.
Quality grows through precise deterministic assertions and separate generated
exploration, rather than larger wall-clock sleeps or retries of failed tests.

The virtual startup regressions distinguish exception/event errors at the
production 2s window minus/plus 1ms, verify cancellation on either side of
handoff, and bound the additional capacity-signal discovery window. They assert
task/timer quiescence before the scheduler teardown can hide a leak.

Reservation tests use one real database and a separate session per contender.
On PostgreSQL/MySQL, barriers retain both stale snapshots before conditional
admission/ownership writes. SQLite exercises its existing writer serialization
without introducing a barrier inside that lock. Replay of either terminal
operation must retain the winning durable counters. Four cases passed locally
on SQLite, MySQL 8.4 and PostgreSQL 16 with isolated xdist databases.

The stronger browser check reproduced a one-frame 48px overflow from a stale
Recharts area width. Local clipping fixes the real defect. The test observes
resize frames, waits for fonts and independent stable geometry, then asserts
containment once. Its existing deadline and zero retry policy are unchanged;
all nine browser scenarios passed after the fix.

The selected 22 properties run at their existing budgets in regular CI and
at least 500 examples under `thorough`; nine pinned examples exercise Unicode,
SSE line boundaries, routing exhaustion and replayed tool/directive fields.
The local extended run passed all 22 properties at seed 20261007, with 500
passing generated cases reported for each. Scheduled/manual runs preserve
seed metadata, test output, JUnit and hidden Hypothesis evidence. The explicit
Bash shell keeps a piped pytest failure from becoming a successful tee result.

Run-specific evidence lives in the ignored `.test-results/quality-20261007/`.
It includes a diagnostic full Vitest run with three timing failures during
concurrent local checks, the successful isolated investigation, and subsequent
verification. Cloud timestamps and conclusions are recorded after publication,
with 6m20s as the prior full-CI baseline. This measurement is evidence, not a
timing-sensitive assertion or a promise that runner latency is constant.
