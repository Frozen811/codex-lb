## ADDED Requirements

### Requirement: WebSocket handoff retains completed downstream receives

An active Responses WebSocket relay MUST retain ownership of its outstanding downstream receive until its result has been consumed exactly once or explicit lifecycle cancellation has cancelled and awaited it. Completing that receive during upstream retirement or handoff MUST NOT cause its queued request, disconnect, or exception to be discarded by creating another receive. Existing idle shutdown, drain, account ownership, retry, and settlement policies MUST remain enforced.

#### Scenario: Queued turn completes during upstream retirement

- **WHEN** a second downstream turn becomes ready while the first upstream connection is being retired after a clean close
- **THEN** the relay consumes and dispatches the queued turn exactly once through the next permitted connection
- **AND** both turns retain their expected response lifecycle and cleanup

#### Scenario: Completed downstream receive is consumed before replacement

- **WHEN** an owned downstream receive is already complete on the next relay polling iteration
- **THEN** its result reaches the normal message, disconnect, or exception handling path
- **AND** a replacement receive is created only after ownership has been cleared
