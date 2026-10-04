## ADDED Requirements

### Requirement: Fair continuous transcript backlog flushing

The HTTP bridge transcript flusher MUST continue bounded passes while eligible nonterminal events remain queued without waiting for the ordinary flush interval between passes. Each pass MUST give every eligible operation a bounded batch opportunity and yield control before repeating. It MUST preserve operation-local event order, owner fencing, queue limits, terminal settlement and shutdown cancellation. A failed optional spool write MUST NOT prevent another operation's eligible backlog from draining.

#### Scenario: Burst spans multiple batches
- **WHEN** one operation queues 320 events with batch size 32
- **THEN** ten ordered writes drain its backlog without nine intervening flush-interval waits

#### Scenario: Competing operations and failed spool
- **WHEN** several operations have queued events and one optional spool write fails
- **THEN** other eligible operations continue bounded fair passes
- **AND** the failed transcript remains ineligible for complete replay
