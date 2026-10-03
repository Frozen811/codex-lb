## ADDED Requirements

### Requirement: TLS reverse-proxy setup explains forwarding trust and transport verification

Reverse-proxy guidance MUST provide a concrete TLS listener adaptation with certificate/key paths and certificate verification enabled on clients. It MUST distinguish forwarding projection trust from application firewall/identity trust and explain trusted source configuration for container proxies. It MUST distinguish HTTP/SSE and WebSocket transport evidence, idle timeout scopes and authenticated product requests from synthetic protocol probes.

#### Scenario: TLS terminates in a trusted reverse proxy

- **WHEN** an operator proxies an HTTPS dashboard request to plain HTTP codex-lb
- **THEN** the guide configures both required trust layers and preserves Host/scheme/client identity
- **AND** client verification uses a matching trusted certificate without disabling validation
