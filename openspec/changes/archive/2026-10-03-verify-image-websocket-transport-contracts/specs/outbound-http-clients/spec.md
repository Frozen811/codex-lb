## ADDED Requirements

### Requirement: Native Responses JSON request compression

Native Codex Responses and compact JSON POSTs MUST use deterministic zstd request-body encoding with a matching Content-Encoding and no stale Content-Length. Their decompressed body MUST equal the prepared JSON bytes. Opaque relay bodies, multipart uploads and Python fallback requests MUST retain their existing representation. Encoding MUST NOT add compression negotiation or request-identity headers.

#### Scenario: Native Responses request reaches an HTTP/2 origin

- **WHEN** a native Responses JSON POST reaches a TLS HTTP/2 origin
- **THEN** its headers advertise zstd and its decoded body equals the prepared JSON
- **AND** native inbound identity and absent compression negotiation are preserved

#### Scenario: Routed native JSON and compact requests

- **WHEN** native egress sends a routed Responses or compact JSON POST
- **THEN** it uses the same body encoding and selected route as the direct path

#### Scenario: Opaque or Python request retains its body

- **WHEN** a request relays raw bytes, uploads multipart data or falls back to the Python client
- **THEN** zstd JSON encoding is not applied to that representation


## MODIFIED Requirements

### Requirement: Native egress upstream client transport parity

The native egress helper MUST provide the specified HTTP/2 and normalized identity transport profile. Outbound HTTP/2 connections MUST use Rustls TLS, an initial stream window size of 2 MiB, and an initial connection window size of 5 MiB. Inbound non-native SDK requests MUST be normalized before dispatch by removing SDK-specific headers (`x-stainless-*`, `x-openai-client-*`) and setting standard Codex CLI persona identity (`User-Agent`, `originator`, and `version`).

#### Scenario: Native egress HTTP/2 client profile matches Codex CLI
- **WHEN** native egress establishes an upstream HTTP/2 connection
- **THEN** the TLS provider is Rustls
- **AND** the HTTP/2 initial stream window size is 2 MiB and initial connection window size is 5 MiB

#### Scenario: Non-native SDK request is rewritten to Codex CLI persona
- **WHEN** an inbound request includes `x-stainless-*` or `x-openai-client-*` headers
- **THEN** those headers are stripped from the upstream request
- **AND** `User-Agent` is normalized to the `codex_cli_rs` persona format
