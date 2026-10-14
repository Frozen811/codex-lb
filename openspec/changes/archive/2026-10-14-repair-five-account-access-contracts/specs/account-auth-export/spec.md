## ADDED Requirements

### Requirement: Codex credential export preserves explicit account identity

Codex-format auth export MUST include the selected account's email, plan type, workspace ID, workspace label and seat type using import-compatible field names. Exporting and reimporting opaque access-only credentials MUST retain the same local slot and workspace identity. Missing ID and refresh tokens MUST remain absent credentials; frontend response validation and export rendering MUST accept null or omitted optional tokens and MUST NOT offer copy controls for absent tokens. OpenCode output MUST retain its existing provider-keyed format.

#### Scenario: Opaque Business credential round-trip
- **WHEN** an operator exports and reimports an opaque access-only Business account with explicit identity
- **THEN** its email, plan and workspace identity remain unchanged
- **AND** the import updates the same local account slot without overwriting a sibling.

#### Scenario: Export without optional credentials
- **WHEN** export contains no ID or refresh token
- **THEN** frontend validation and the export dialog succeed
- **AND** downloaded JSON preserves null credentials without fabricated strings or copy controls.
