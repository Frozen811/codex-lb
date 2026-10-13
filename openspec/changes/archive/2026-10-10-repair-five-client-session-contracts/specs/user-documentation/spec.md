## ADDED Requirements

### Requirement: Ordinary Codex provider examples declare standalone search

The ordinary `codex-lb` provider examples in both READMEs, the client guide and downloadable configuration MUST declare `supports_standalone_web_search = true` with the minimum codex-lb version. Documentation MUST distinguish the provider capability from live-search preference and the experimental standalone-search feature flag. Separate Daybreak examples MUST retain their own capability policy.

#### Scenario: Ordinary search examples remain consistent
- **WHEN** the five ordinary provider examples are parsed as TOML
- **THEN** all five enable standalone search and retain valid provider configuration
- **AND** the separate Daybreak provider remains unchanged

#### Scenario: Search setup names separate controls
- **WHEN** an operator follows the native search guide
- **THEN** it explains the minimum version, live-search preference and separate experimental flag
