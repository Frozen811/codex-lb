## ADDED Requirements

### Requirement: Ring membership database work stops cooperatively during shutdown

Shutdown MUST signal the owned ring registration/retry/heartbeat task to stop. Within the existing background stop grace, active registration or heartbeat database work MUST finish before membership is marked stale or database engines are disposed. Idle interval and registration retry waits MUST wake promptly on stop and MUST NOT start another database operation after observing it. Work exceeding the existing bounded stop/cancellation budget MUST remain tracked as incomplete for the clean-shutdown proof; it MUST NOT extend the process shutdown deadline.

#### Scenario: SIGTERM during ring registration
- **WHEN** SIGTERM arrives while registration holds a database operation that can finish within grace
- **THEN** the operation and connection cleanup complete before stale marking/disposal
- **AND** shutdown emits no SQLAlchemy pool reset/close error caused by immediate cancellation

#### Scenario: Idle or failed-registration retry is stopping
- **WHEN** the owned ring task is waiting for its heartbeat interval or registration retry delay and shutdown requests stop
- **THEN** it wakes promptly without waiting for the full interval or starting another database operation

#### Scenario: Ring database operation cannot drain within budget
- **WHEN** ring database work remains pending beyond the bounded stop grace and cancellation wait
- **THEN** shutdown proceeds under the existing process deadline with that work tracked as incomplete
- **AND** it does not record a clean SQLite shutdown while the tracked work remains pending
