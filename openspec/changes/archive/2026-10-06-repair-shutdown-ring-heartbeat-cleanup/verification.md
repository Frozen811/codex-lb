# Shutdown ring heartbeat verification

Date: 2026-10-06, Europe/Kiev. Parent main `daf67afb78eab9537bfac57bcb4d1c7db1267d04`. Publication/CI repair is explicitly authorized by the user. This change addresses a newly reproduced runtime shutdown defect; it does not change or re-close the earlier registry task selection.

## Root cause and red evidence

The main CI run 37465856821 failed once with `Exception during reset` in the six-run startup/SIGTERM smoke test, and again on attempt 2 with `Exception closing connection` after the held poller read had completed. A single isolated run on Python 3.14 and then Python 3.13 passed, so a retry alone did not establish a repair.

A constrained Linux/Python **3.13.15**, frozen-lock, source-overlay reproduction with **0.5 CPU** identified the owner via a temporary SQLAlchemy logging hook: `lifespan.<locals>._register_and_heartbeat`. Baseline runs 0/1 passed; run 2 failed during SQLite NullPool/aiosqlite close with CancelledError. Lifespan used immediate Task.cancel on the ring task. Raw bootstrap credentials were not copied into evidence.

New real-process registration barrier: hold the ring INSERT until SIGTERM commits, release it 0.5s later, and require completion before stale marking/disposal. On the old parent source this deterministically failed: **ring DB operation was interrupted by cancellation**. The existing exit bound and pool-error checks are preserved.

## Implementation and green evidence

- One lifespan-owned stop event wakes heartbeat intervals and registration retry delays. The task finishes its current operation, observes stop before another DB/maintenance unit, and uses the existing stop_task_after_grace helper before membership stale marking.
- Registration/advertise phases check stop between operations and do not publish ready registration after observing shutdown. No new setting, dependency, migration or routing change.
- Existing bounded fallback/incomplete-task tracking and SQLite clean-marker gate remain authoritative. No process deadline is extended.
- `uv run pytest -q tests/unit/test_otel.py tests/unit/test_graceful_shutdown.py tests/unit/test_scheduler_task_shutdown.py tests/unit/test_shutdown_drain_bounds.py --tb=line --show-capture=no`: **128 passed**. Idle and failed-registration retry variants assert the owned ring task finishes without cancellation; background grace, deadline and incomplete-drain controls remain covered.
- Linux/Python **3.13.15**, frozen dependencies, 0.5 CPU, parent Git source with only current main.py and shutdown test overlays: **3 real-process integration tests passed** in 127.79s. Includes six prompt SIGTERM samples, held cache-poller read and held ring registration; stale membership, leader release, no pool errors and bounded exit all asserted.
- Additional constrained **24/24** prompt SIGTERM startups passed with **zero pool errors, zero scheduler_leader rows**. Maximum exit **1.694s**, below the retained **5s** contract. Python 3.13.15 is the available local runtime; exact cloud Python 3.13.16 is verified by the successor CI run, not claimed by this local evidence.
- Full Ruff check/format (**1471 files**) and full ty passed. Proxy architecture, cancellation safety, timing seams, settings **98/98**, migration topology/single existing head, simplicity budgets and whitespace checks passed.
- Strict OpenSpec change validation passed; canonical specs **68/68**. One requirement/three scenarios exact-synchronized to graceful-shutdown; stable context records rationale, failure, budget and example.

Completeness/correctness/coherence: active DB registration maps to the red/green real SIGTERM barrier and constrained stress; idle/retry maps to portable lifespan task-completion assertions; wedged/deadline behavior reuses the existing stop-helper tests and clean-marker guard. No critical findings remain in the local scope.

## Publication boundary

Local implementation is verified and ready for archive/commit. The user turn remains active until the successor main revision's entire CI matrix and other applicable checks complete successfully. Cloud outcomes are recorded against the exact published SHA separately; earlier failed attempts and skip/xfail limitations are not converted into success claims. No production deployment or release is performed.
