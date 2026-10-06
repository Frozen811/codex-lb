## ADDED Requirements

### Requirement: Parallel tests isolate mutable resources

The test harness SHALL schedule Python tests by file in independent workers.
Each worker MUST own its SQLite file or disposable PostgreSQL/MySQL database.
Concurrent xdist invocations MUST NOT share worker database names. Database URLs MUST be
resolved before importing the application's engine and inherited by spawned
processes. Automatic worker counts MUST respect CPU availability and memory limits.

#### Scenario: Multiple workers execute database tests

- **WHEN** database tests run concurrently
- **THEN** schema resets in one worker do not affect another worker
- **AND** worker resources are disposed after the session

#### Scenario: Windows starts a fresh interpreter

- **WHEN** a test uses the spawn multiprocessing context
- **THEN** the child uses its parent's isolated database URL
- **AND** ASGI requests execute without requiring fork or Bash syntax

### Requirement: CI shares builds and balances integration work

CI SHALL publish one dashboard build artifact for the current run and reuse it
in pytest, browser, and packaging jobs. Six integration-core shards MUST partition
the selected files exactly once, preserve stable required check contexts, and use
recorded file durations when supplied, with deterministic estimates for new files.
Frontend PR tests MUST execute without coverage instrumentation. Vitest workers
MUST isolate module and DOM state and clear per-test mocks and request handlers.

#### Scenario: A backend pull request runs integration tests

- **WHEN** CI evaluates backend changes
- **THEN** all six integration-core shards consume the same build and duration input
- **AND** any failed shard fails the integration-core required check

#### Scenario: An unrelated pull request skips expensive tests

- **WHEN** no backend paths changed
- **THEN** required pytest contexts still succeed through their placeholder steps
- **AND** a skipped dashboard build does not suppress these contexts
