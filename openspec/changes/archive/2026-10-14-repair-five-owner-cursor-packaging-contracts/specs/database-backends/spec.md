## ADDED Requirements

### Requirement: Cancelled SQLite writes release traceback-retained cursors

Closing a SQLite request or background connection MUST finalize live statement cursors even when cancellation tracebacks retain them. Cursor tracking MUST NOT extend their lifetime. Cleanup MUST attempt every cursor and the connection after an individual close error and then report the first cleanup error. Cancellation and rollback semantics MUST remain intact, and no garbage collection or process restart MUST be required to release the writer lock. PostgreSQL, MySQL and in-memory database behavior MUST remain compatible.

#### Scenario: A cancelled RETURNING write retains its traceback
- **WHEN** a file-backed SQLite write is cancelled while executing a RETURNING statement and its traceback is retained after teardown
- **THEN** an independent writer can write to that file without garbage collection
- **AND** the cancelled write is rolled back

#### Scenario: A terminal spool append times out
- **WHEN** a rows_v1 or chunks_v2 terminal append times out on SQLite
- **THEN** subsequent bridge settlement and leader writes can finish after teardown
- **AND** the failed spool is incomplete and rejects late append attempts

#### Scenario: One cursor fails to close
- **WHEN** one tracked cursor raises during connection cleanup
- **THEN** every remaining cursor and the connection still receive a close attempt
- **AND** the first cleanup error is reported after those attempts
