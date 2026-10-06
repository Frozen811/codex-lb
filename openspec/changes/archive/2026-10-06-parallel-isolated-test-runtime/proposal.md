## Why

Sequential pytest and Vitest runs, count-only integration shards, and repeated
dashboard builds extend feedback time. Parallel execution must preserve database,
mock, and process isolation on Linux and Windows.

## What Changes

- Run pytest files in isolated xdist workers with bounded automatic concurrency.
- Use worker-specific temporary SQLite storage and disposable server databases.
- Run isolated Vitest thread workers and clean up mocks between tests.
- Balance six integration shards using recorded durations with static estimates
  for new files, and reuse one dashboard build artifact in CI consumers.
- Provide direct PowerShell-compatible pytest commands and record repeatable timings.

## Impact

Test infrastructure, Makefile, GitHub Actions, and contributor documentation.
Production behavior and database migrations are unchanged.
