## ADDED Requirements

### Requirement: Internal drain status reports request-persistence activity

The `/internal/drain/status` endpoint MUST surface detached request-persistence activity alongside `in_flight` and bridge activity counters. The response payload `checks` dictionary MUST include `request_persistence_pending` (count of unfinished persistence tasks), `request_persistence_active` (boolean indicating whether any persistence tasks remain unfinished), `api_key_settlements_pending` (count of unfinished API-key reservation and settlement tasks), and `persistence_drain_active` (boolean indicating whether persistence work is currently blocking completion of drain).

#### Scenario: Internal drain status reflects pending persistence tasks

- **GIVEN** a server undergoing graceful drain with zero in-flight responses
- **WHEN** detached background persistence or API-key settlement tasks are still executing
- **THEN** `/internal/drain/status` reports `request_persistence_pending` as the number of running tasks
- **AND** reports `request_persistence_active = "true"` and `persistence_drain_active = "true"`

#### Scenario: Internal drain status reflects settled persistence tasks

- **GIVEN** a server undergoing graceful drain with zero in-flight responses
- **WHEN** all background persistence and settlement tasks have completed
- **THEN** `/internal/drain/status` reports `request_persistence_pending = "0"`
- **AND** reports `request_persistence_active = "false"` and `persistence_drain_active = "false"`
