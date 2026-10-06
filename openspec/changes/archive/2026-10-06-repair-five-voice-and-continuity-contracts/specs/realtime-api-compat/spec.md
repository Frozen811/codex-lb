## ADDED Requirements

### Requirement: Desktop voice setup documents both private endpoint overrides

The Live Voice setup documentation SHALL show both experimental client endpoint overrides as top-level TOML settings: call creation targeting the proxy's `/backend-api/codex` base and the authenticated voice sideband targeting its `/v1` base. It MUST distinguish these from Responses provider configuration and server environment settings, identify experimental client compatibility limits, and require call creation, sideband acceptance, transcript, backend handoff and audible response for a live end-to-end claim. WebRTC media MUST remain described as direct client-to-upstream traffic.

#### Scenario: Custom provider uses a v1 Responses base
- **WHEN** an operator follows the documented Desktop voice example
- **THEN** call creation and sideband bases are configured independently at TOML root
- **AND** documentation does not promise that Responses WebSocket support configures voice

#### Scenario: Only call creation has been tested
- **WHEN** local route tests pass without a live Desktop voice session
- **THEN** evidence states the local route and documentation scope without claiming live media or audio success
