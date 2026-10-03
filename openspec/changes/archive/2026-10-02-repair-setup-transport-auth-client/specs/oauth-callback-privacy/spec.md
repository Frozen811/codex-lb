## ADDED Requirements

### Requirement: Failed callback listener startup releases resources and preserves manual recovery

An OAuth callback listener whose startup fails or is cancelled MUST release resources acquired by that startup before propagating the failure or cancellation. An occupied callback port MUST retain the existing pending browser flow's manual-callback recovery path and MUST emit a warning identifying the bind host, port and exception type without code, verifier, state, authorization URL or callback query values.

#### Scenario: Callback port is already occupied

- **WHEN** a browser OAuth flow cannot bind its callback port
- **THEN** initialized listener resources are released
- **AND** the flow remains usable for manual callback with a safe warning

#### Scenario: Listener startup is cancelled

- **WHEN** callback listener startup is cancelled after resource initialization
- **THEN** acquired listener resources are released and cancellation propagates
