## ADDED Requirements

### Requirement: Terminal append remains owned after bounded delivery wait
The HTTP bridge MUST bound its wait for terminal persistence without cancelling an in-flight append when the wait expires or its caller is cancelled. The batcher MUST retain task ownership until completion or shutdown. Timeout MUST require fallback settlement, MUST NOT authorize transcript replay and MUST NOT allow a late append to overwrite a settled operation or clear a newer attempt's state.

#### Scenario: SQLite writer at the delivery bound
- **WHEN** terminal persistence is blocked inside an SQLite write statement beyond the wait bound
- **THEN** downstream delivery proceeds with settlement required
- **AND** releasing the statement permits the append to finish and a second connection to acquire a writer transaction

#### Scenario: Caller cancellation and late settlement
- **WHEN** the caller is cancelled during the bounded wait
- **THEN** cancellation reaches the caller while persistence remains owned
- **AND** a late append after fallback settlement cannot make the spool replayable

### Requirement: CCodex gateway identities preserve native fingerprints
The shared native Codex classifier MUST recognize exactly ccodex-internal and ccodex-handoff-worker originators and their slash-delimited User-Agent prefixes. HTTP and WebSocket upstream requests MUST preserve their inbound identity and version. Arbitrary lookalike prefixes and continuity headers alone MUST NOT grant native classification.

#### Scenario: Gateway relays stock Codex traffic
- **WHEN** either gateway identity is supplied through originator or User-Agent
- **THEN** HTTP and WebSocket header construction preserves that native fingerprint

#### Scenario: Unknown gateway lookalike
- **WHEN** an SDK request supplies an unknown gateway-like identity or only continuity headers
- **THEN** normal non-native fingerprint normalization applies

