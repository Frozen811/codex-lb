# outbound-http-clients Specification Delta

## ADDED Requirements

### Requirement: Native egress upstream client transport parity

The native egress helper MUST mirror the HTTP transport characteristics of the official Codex client to prevent fingerprint divergence. Outbound HTTP/2 connections MUST use Rustls TLS, an initial stream window size of 2 MiB, and an initial connection window size of 5 MiB. Inbound non-native SDK requests MUST be normalized before dispatch by removing SDK-specific headers (`x-stainless-*`, `x-openai-client-*`) and setting standard Codex CLI persona identity (`User-Agent`, `originator`, and `version`).

#### Scenario: Native egress HTTP/2 client profile matches Codex CLI
- **WHEN** native egress establishes an upstream HTTP/2 connection
- **THEN** the TLS provider is Rustls
- **AND** the HTTP/2 initial stream window size is 2 MiB and initial connection window size is 5 MiB

#### Scenario: Non-native SDK request is rewritten to Codex CLI persona
- **WHEN** an inbound request includes `x-stainless-*` or `x-openai-client-*` headers
- **THEN** those headers are stripped from the upstream request
- **AND** `User-Agent` is normalized to the `codex_cli_rs` persona format
