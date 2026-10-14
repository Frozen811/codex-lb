## ADDED Requirements

### Requirement: Native WebSocket bursts preserve bounded output and acknowledgement progress

The service MUST preserve FIFO output from a valid burst of at least 65 native WebSocket messages while the consumer is temporarily delayed. Buffering MUST have a finite event cap and an accumulated payload byte budget that includes UTF-8 text, binary data and interpreted Responses payload copies. A lone large frame MUST retain the existing configured frame-size compatibility. Send acknowledgements MUST continue independently of data consumption. Overflow MUST terminate and finalize the socket once, fail pending sends, and surface a consumer_backpressure failure after accepted output; cancellation, reader failure and close MUST retain terminal ownership and cleanup.

#### Scenario: Burst and send acknowledgement before receive

- **WHEN** 65 valid frames arrive before any receive and a send acknowledgement follows
- **THEN** the send completes and all 65 frames are received in order without abort

#### Scenario: Payload budget or event cap exceeded

- **WHEN** the consumer stops draining and either bounded capacity is exceeded
- **THEN** accepted frames precede one consumer_backpressure terminal, pending sends fail and the request is finalized once

### Requirement: Exact CCodex identities retain their upstream fingerprint

The service MUST preserve originator, User-Agent and version for exactly ccodex-internal and ccodex-handoff-worker identities through compatible HTTP and native WebSocket Responses routes, including supported aliases. Unlisted CCodex lookalikes MUST remain non-native. Identity classification MUST NOT override inference transport policy. Package installation MUST require urllib3 2.8.0 or newer.

#### Scenario: Known CCodex identity reaches upstream

- **WHEN** an HTTP or native WebSocket request carries a known CCodex originator or matching User-Agent prefix
- **THEN** the upstream fingerprint retains those supplied identity headers and the configured transport policy still applies

#### Scenario: Unlisted lookalike remains normalized

- **WHEN** a request carries an unlisted CCodex identity and continuity headers
- **THEN** it remains non-native and receives the existing upstream fingerprint normalization
