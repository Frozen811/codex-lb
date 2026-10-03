## ADDED Requirements

### Requirement: Client setup identifies authentication and endpoint contracts

Client setup documentation MUST distinguish a Codex LB API key from dashboard credentials and upstream ChatGPT credentials. It MUST identify generation-provider, catalog and usage base URL suffixes consistently across the guide and shipped examples, and label the tested client version and synthetic versus live upstream evidence. Client instructions MUST NOT contain merge-conflict markers or promise conversation synchronization from provider identity alone.

#### Scenario: Configure an API-key Codex CLI provider

- **WHEN** an operator configures a key-authenticated Codex CLI provider
- **THEN** the guide identifies the key environment and provider's selected auth mode
- **AND** generation, catalog and usage URLs refer to the selected deployment with their required suffixes
