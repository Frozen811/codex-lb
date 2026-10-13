## ADDED Requirements

### Requirement: Local SQLite write admission belongs to its task

File-backed SQLite write admission MUST permit nested writes by the admitted task and MUST serialize writes performed by a different task, including a task created inside the admitted context. Cancellation of a waiting task MUST NOT release another task's admission. Scheduler lease writes MUST use the same admission while preserving database-clock expiry guards and releasing their transaction before admission ends. PostgreSQL and in-memory SQLite MUST retain their existing concurrency semantics.

#### Scenario: A child writes after its parent
- **WHEN** an admitted task starts a child that writes to the same file-backed SQLite store
- **THEN** the child waits until the parent leaves admission
- **AND** same-task nested writes remain permitted.

#### Scenario: Waiting writer is cancelled
- **WHEN** a different task is cancelled while waiting for admission
- **THEN** the admitted task retains ownership and a subsequent writer can enter after it leaves.

#### Scenario: Lease resumes after contention
- **WHEN** scheduler lease acquisition or renewal waits behind a local writer
- **THEN** it completes using the database execution clock after admission
- **AND** an expired lease cannot be resurrected.

### Requirement: Authentication and fingerprint writes share SQLite admission

Database-backed authentication attempt mutations, OAuth flow persistence and fingerprint stamping MUST serialize with other admitted local file-backed SQLite writers. OAuth and fingerprint operations that own their sessions MUST finish commit or rollback and session cleanup before releasing admission. OAuth upstream network work MUST NOT hold write admission. Existing rate-limit errors, monotonic OAuth terminal status, fingerprint mismatch refusal and bounded external lock retries MUST remain unchanged.

#### Scenario: Authentication waits behind a local writer
- **WHEN** login attempt writes or OAuth flow persistence arrive while a local SQLite writer owns admission
- **THEN** they wait and complete after that writer releases its transaction
- **AND** temporary local contention does not become an HTTP 500.

#### Scenario: Fingerprint verification waits behind a local writer
- **WHEN** startup verifies a fingerprint while a local writer owns admission
- **THEN** verification waits and succeeds for a matching fingerprint after release
- **AND** a mismatched fingerprint still refuses enforce-mode startup.

### Requirement: Reclamation cancellation preserves connection cleanup

Cancellation during interruption of a wedged SQLite connection MUST be deferred until captured open connections have received their invalidation attempt and late teardown callbacks have been registered. Driver interruption failure MUST NOT suppress invalidation or cleanup ownership. Cancellation MUST propagate after those attempts. Completed, closed, PostgreSQL and in-memory teardown behavior MUST remain unchanged.

#### Scenario: Cancellation arrives during interruption
- **WHEN** the reclaim caller is cancelled while awaiting driver interruption
- **THEN** invalidation and late-close ownership still complete
- **AND** cancellation propagates afterward without leaving a stale cleanup registration.

#### Scenario: Interruption reports an already-closed driver
- **WHEN** the driver interrupt raises a closed-database error for a captured connection
- **THEN** invalidation is still attempted and the abandoned teardown remains owned until completion
- **AND** cleanup failure diagnostics do not claim guaranteed writer release.

## MODIFIED Requirements

### Requirement: Startup sentinel writes tolerate and name transient SQLite lock contention

The startup writes that insert-if-absent into `runtime_sentinels` — the encryption-key fingerprint stamp and the hard-sticky outage-grace seed — MUST retry a transient SQLite lock failure (`database is locked` / `database is busy`) on one shared bounded budget of three retries totalling under one second, and MUST reset a session whose transaction the failed attempt left dirty before the next attempt. Fingerprint stamping MUST wait for local file-backed SQLite writer admission before opening its attempt session and MUST finish transaction/session cleanup before releasing admission. Startup-fresh connections do not remove contention from external writers. A lock failure that outlives the budget MUST preserve the call site's existing outcome rather than newly degrading or newly failing startup, and an `OperationalError` that is not a lock failure MUST propagate without being retried, so the seed's existing not-yet-migrated (`no such table`) degrade to a no-op still applies. Exhausting the budget MUST be reported at WARNING, and each retry at DEBUG, with the driver's extended result-code name (`sqlite_errorname`, or its absence) and the elapsed time — the two mechanisms behind `database is locked` are otherwise indistinguishable, since `SQLITE_BUSY_SNAPSHOT` returns immediately while `SQLITE_BUSY` returns only after the full busy timeout. These reports MUST NOT include the values being written.

#### Scenario: A transient lock on the outage-grace seed is retried
- **GIVEN** the startup hard-sticky outage-grace seed whose sentinel stamp fails once with `database is locked`
- **WHEN** startup runs the seed
- **THEN** the failed transaction is rolled back and the stamp is retried within the shared budget
- **AND** the backfill completes on the retry

#### Scenario: A lock that outlives the budget keeps the existing outcome
- **GIVEN** a startup sentinel write whose every attempt within the budget fails with `database is locked`
- **WHEN** the budget is exhausted
- **THEN** the failure propagates and startup fails, as it did before the retry existed

#### Scenario: A non-lock operational error is not retried
- **GIVEN** a database whose `runtime_sentinels` table does not exist yet
- **WHEN** the outage-grace seed runs
- **THEN** the error is not retried
- **AND** the seed rolls back and returns without stamping, exactly as before

#### Scenario: The give-up report classifies the lock failure
- **GIVEN** a startup sentinel write that exhausts its retry budget
- **WHEN** the exhaustion is reported
- **THEN** the report names the write, the driver's `sqlite_errorname` (or its absence), and the elapsed time
- **AND** the report contains none of the values the write was stamping

