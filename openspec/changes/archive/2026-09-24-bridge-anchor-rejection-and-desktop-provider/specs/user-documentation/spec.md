# user-documentation Specification Delta

## MODIFIED Requirements

### Requirement: README stays a quickstart

`README.md` SHALL remain a slim quickstart: hero screenshots, feature summary, Quick Start, a single in-README client configuration path (Codex CLI) with a table linking other clients to the docs site, configuration and data pointers, documentation links, and development notes. Detailed operational content (auth modes, routing guide, database runbooks, Kubernetes, remote setup, per-client walkthroughs, Codex Desktop built-in provider preservation) SHALL live on the documentation site instead. The README SHALL carry a prominent link to the documentation site and SHALL keep the all-contributors generated block between its `ALL-CONTRIBUTORS-LIST` markers. `README.zh-CN.md` SHALL carry a banner identifying the English documentation site as canonical.

#### Scenario: Moved content is reachable from the README

- **WHEN** a reader looks for content removed from the README (e.g. the Postgres 16→18 upgrade runbook)
- **THEN** the README links to the documentation site where that content now lives

#### Scenario: Contributors block survives the diet

- **WHEN** the all-contributors bot regenerates the contributors table
- **THEN** the `ALL-CONTRIBUTORS-LIST:START`/`:END` markers still exist in `README.md` and the update applies cleanly

#### Scenario: Codex Desktop built-in provider documentation is available in docs

- **WHEN** an operator or user configures Codex Desktop to route through codex-lb while preserving the built-in OpenAI provider
- **THEN** the documentation site provides configuration examples showing how to override `[model_providers.openai]`
- **AND** the README remains focused on quickstart instructions without expanding into custom provider runbooks
