## MODIFIED Requirements

### Requirement: Multi-replica deployments require shared PostgreSQL coordination

Running more than one application replica SHALL require: a shared PostgreSQL database through which all cross-replica coordination flows (`scheduler_leader` lease, `bridge_ring_members`, `http_bridge_sessions`, `cache_invalidation`, `sticky_sessions`, `runtime_sentinels`); leader election enabled (`CODEX_LB_LEADER_ELECTION_ENABLED`, which defaults to `true`) so singleton schedulers run on exactly one replica; a unique instance id and a reachable replica-specific advertise URL per replica for bridge owner forwarding; and identical encryption key material provided by `CODEX_LB_ENCRYPTION_KEY` or a mounted key file on every replica. Explicitly setting `CODEX_LB_LEADER_ELECTION_ENABLED=false` is the single-instance escape hatch that makes every replica treat itself as leader and MUST NOT be used with more than one replica.

#### Scenario: Supported two-replica topology

- **GIVEN** two replicas configured with the same PostgreSQL `CODEX_LB_DATABASE_URL`
- **AND** `CODEX_LB_LEADER_ELECTION_ENABLED` at its default (`true`) on both replicas
- **AND** each replica has a unique bridge instance id with a reachable replica-specific advertise URL
- **AND** both replicas use the same environment key or mounted encryption key file
- **WHEN** both replicas start
- **THEN** exactly one replica acquires the scheduler leader lease and runs singleton schedulers
- **AND** hard-continuity bridge requests landing on the non-owner replica are forwarded to the owner

#### Scenario: Leader election left at its default preserves the singleton guarantee

- **GIVEN** two replicas sharing one PostgreSQL database
- **AND** `CODEX_LB_LEADER_ELECTION_ENABLED` is left at its default (enabled)
- **WHEN** both replicas start
- **THEN** exactly one replica acquires the lease and runs singleton schedulers
- **AND** the operator observes no duplicate upstream polling (usage refresh, automations, retention)
- **AND** explicitly setting `CODEX_LB_LEADER_ELECTION_ENABLED=false` is the single-instance escape hatch that makes every replica treat itself as leader and run singleton schedulers N-fold

### Requirement: Startup verifies encryption-key consistency against the shared database

At startup, after schema readiness, each replica SHALL compute a fingerprint of its encryption key and atomically stamp it into `runtime_sentinels` (insert-if-absent), then compare its local fingerprint against the stored sentinel. When `CODEX_LB_ENCRYPTION_KEY_FINGERPRINT_MODE=enforce` (the default), a replica whose fingerprint differs from the stored sentinel SHALL refuse to start with an error naming both fingerprint prefixes and remediation using either the same `CODEX_LB_ENCRYPTION_KEY` value or the same mounted key file without disclosing key material; `warn` mode SHALL log an ERROR and continue; `off` SHALL disable the check.

#### Scenario: First boot stamps the sentinel

- **GIVEN** an empty `runtime_sentinels` table
- **WHEN** a replica starts
- **THEN** it stamps `sha256` of its encryption key as the `encryption_key_fingerprint` sentinel and starts normally

#### Scenario: Matching replica starts

- **GIVEN** a stamped `encryption_key_fingerprint` sentinel
- **WHEN** a second replica with the same encryption key starts
- **THEN** the fingerprint comparison passes and startup proceeds

#### Scenario: Divergent-key replica refuses to start in enforce mode

- **GIVEN** a stamped `encryption_key_fingerprint` sentinel
- **AND** `CODEX_LB_ENCRYPTION_KEY_FINGERPRINT_MODE` is `enforce`
- **WHEN** a replica with a different encryption key starts
- **THEN** startup fails with an error naming both fingerprint prefixes
- **AND** the error names the remediation (use the shared environment key or mount the shared key; after an intentional rotation, delete the sentinel row or set the mode to `warn`)

#### Scenario: Divergent-key replica continues in warn mode

- **GIVEN** a stamped `encryption_key_fingerprint` sentinel
- **AND** `CODEX_LB_ENCRYPTION_KEY_FINGERPRINT_MODE=warn`
- **WHEN** a replica with a different encryption key starts
- **THEN** an ERROR is logged and startup continues

#### Scenario: Concurrent first boot of two divergent replicas

- **GIVEN** an empty `runtime_sentinels` table
- **WHEN** two replicas with different encryption keys run the startup check concurrently
- **THEN** exactly one replica stamps the sentinel
- **AND** the other replica's comparison fails against the stamped value


## ADDED Requirements

### Requirement: Shared encryption key supports stateless replicas

The service MUST accept a valid Fernet key from `CODEX_LB_ENCRYPTION_KEY`, normalize surrounding whitespace, and use it instead of the configured default key file without creating or reading that file. Invalid non-empty environment keys MUST fail settings validation. With the environment absent or blank, the existing key-file behavior MUST remain available. Explicit programmatic key bytes MUST take precedence over an explicit key file; an explicit key-file argument MUST take precedence over the environment key. Encryption and startup fingerprint calculation MUST select the same key material. Independently constructed instances using the same key MUST decrypt each other's persisted ciphertext; a different key MUST fail the enforced shared-database fingerprint check without replacing the sentinel.

#### Scenario: Stateless environment key avoids file access

- **GIVEN** a valid environment key and an unusable default key-file path
- **WHEN** credentials are imported and read by independently constructed encryptors
- **THEN** the persisted ciphertext decrypts with the environment key and no key file is created
- **AND** the startup fingerprint is computed from that same selected key

#### Scenario: Explicit overrides retain precedence

- **GIVEN** distinct environment, explicit file, and explicit byte keys
- **WHEN** a caller provides an explicit file or explicit key bytes
- **THEN** the explicit file wins over the environment and explicit bytes win over both

#### Scenario: Invalid or divergent environment key refuses use

- **WHEN** an invalid non-empty environment key is configured
- **THEN** settings validation fails
- **WHEN** a valid different environment key checks an existing database sentinel in enforce mode
- **THEN** the check fails and leaves the original sentinel unchanged
