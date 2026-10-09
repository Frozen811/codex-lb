## ADDED Requirements

### Requirement: Optional maintenance cannot block ring renewal
After registration, periodic ring renewal MUST be independent of durable ownership reconciliation, stale-operation cleanup, idle-session sweeping and cap-partition refresh. Each optional phase MUST have at most one in-flight invocation, MUST retry ordinary failures on its next cadence and MUST stop starting work after observing shutdown. Ring database operations MUST use background connection admission rather than the request pool. Shutdown MUST stop all phase owners before stale marking and engine disposal; cancellation-resistant owners MUST remain visible to clean-shutdown checks.

#### Scenario: One maintenance phase is blocked
- **WHEN** a durable reconciliation pass cannot complete
- **THEN** heartbeat, idle sweeping, stale-operation cleanup and cap refresh continue independently
- **AND** no second reconciliation pass starts while the first is pending

#### Scenario: A maintenance pass fails
- **WHEN** one optional phase raises an ordinary exception
- **THEN** other phase owners continue and the failed phase retries on its next cadence

#### Scenario: Shutdown interrupts independent phase owners
- **WHEN** shutdown begins with optional maintenance in flight
- **THEN** each phase stops cooperatively within the existing bounded stop policy
- **AND** incomplete work prevents a clean-shutdown claim
