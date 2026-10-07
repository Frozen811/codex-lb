## Why

The isolated MySQL CI slice takes 12m 27s and determines the full workflow's
13m 21s critical path. Three independent runners can share that work while
retaining the same selected tests and worker-database isolation.

## What Changes

- Keep one canonical manifest for the current MySQL file/node selection.
- Partition file groups into three deterministic, duration-weighted shards.
- Retain the complete local `make test-mysql` target and add three shard targets.
- Run a three-entry MySQL matrix with per-shard JUnit artifacts.
- Preserve the existing MySQL required context through a strict aggregate.
- Verify selection integrity, CI dependencies, and actual cloud timings.

## Impact

Test selection, Makefile, GitHub Actions and github-automation documentation.
Application behavior and database isolation semantics remain unchanged.
