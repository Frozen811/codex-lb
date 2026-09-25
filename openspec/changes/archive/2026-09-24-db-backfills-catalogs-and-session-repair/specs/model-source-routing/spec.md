# Model Source Routing Specification Delta

## Requirements

### Requirement: CLIProxyAPI catalog discovery and unavailable model ownership retention

Model sources configured with external catalog discovery (CLIProxyAPI) MUST support automated catalog synchronization and unavailable model ownership retention:
1. When catalog synchronization runs, the source SHALL query the provider's `/v1/models` catalog.
2. In the event of an upstream outage, the system SHALL preserve the last successfully observed model catalog snapshot.
3. Models omitted from an upstream catalog update MUST be retained in the model registry marked as unavailable rather than removed. Requests for omitted models MUST return model unavailability errors rather than falling through to native subscription accounts.

#### Scenario: Unreachable catalog preserves last known snapshot
- **GIVEN** a model source with a cached catalog snapshot
- **WHEN** the external catalog endpoint is temporarily unreachable
- **THEN** the model registry retains the existing model snapshot without dropping models

#### Scenario: Omitted external model retains ownership and rejects fallback
- **GIVEN** a model previously registered to an external model source
- **WHEN** an updated catalog snapshot omits that model
- **THEN** the model is retained as unavailable
- **AND** client requests for that model do not route to subscription accounts
