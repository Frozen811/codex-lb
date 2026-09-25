# telemetry Specification Delta

## ADDED Requirements

### Requirement: Telemetry transmission and opt-out synchronization

The telemetry sender MUST synchronize snapshot transmissions and opt-out events to prevent race conditions (TOCTOU). When an opt-out event is processed, any in-flight snapshot transmission MUST re-check consent atomically before transmission and abort if consent is no longer active. Furthermore, opt-out event payloads MUST accept ISO-8601 strings or datetime objects, and requesting a telemetry preview while telemetry is disabled by environment configuration MUST NOT create or persist a telemetry identity in the database.

#### Scenario: Snapshot transmission aborts when opt-out occurs concurrently

- **GIVEN** a pending telemetry snapshot transmission
- **WHEN** an opt-out event is dispatched concurrently
- **THEN** consent re-check under the transmission lock observes that telemetry is disabled
- **AND** the snapshot POST is aborted

#### Scenario: Telemetry preview under env kill switch does not write identity

- **GIVEN** telemetry is disabled via environment configuration (`CODEX_LB_TELEMETRY_ENABLED=false`)
- **WHEN** the dashboard settings endpoint is queried for telemetry status or preview
- **THEN** no instance identity is generated or saved to the database
