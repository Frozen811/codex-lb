## ADDED Requirements

### Requirement: Bridge signing uses the configured shared encryption key

Internal bridge request signing and verification MUST use the configured encryption key. A nonempty `CODEX_LB_ENCRYPTION_KEY` MUST take precedence over `CODEX_LB_ENCRYPTION_KEY_FILE` without reading or creating a file key. With no environment key, the configured file key MUST be used. Replicas sharing the effective key MUST accept each other's authentic forwards; a replica with a different effective key MUST reject the signature before forwarding upstream.

#### Scenario: Shared environment key and distinct file keys
- **WHEN** two replicas share an environment key and have distinct configured file keys
- **THEN** the receiver accepts the signed request using the environment key and the file keys remain unchanged

#### Scenario: File-only shared key
- **WHEN** replicas have no environment key and share the configured file key
- **THEN** the receiver accepts the signed request

#### Scenario: Mismatched effective key
- **WHEN** the receiver's effective key differs from the signing replica's key
- **THEN** signature verification refuses the forward
