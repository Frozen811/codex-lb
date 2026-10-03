## ADDED Requirements

### Requirement: Fork installation links identify their source and channel

Fork entry points and deployment guides MUST direct installation and configuration readers to fork-owned documentation. Links to upstream issues, contributors, third-party tools or comparative upstream documentation MUST retain their actual ownership and be identifiable as such. Install examples MUST distinguish upstream PyPI from fork source and historical fork release artifacts. A fork download URL MUST NOT be advertised as available until that artifact exists and its identity has been checked. Public metadata discrepancies MUST remain recorded as unresolved until the public resource is rechecked after correction.

#### Scenario: Reader follows a fork installation guide

- **WHEN** a reader follows an installation or client configuration link from either README
- **THEN** the link resolves to the fork's corresponding documentation source
- **AND** historical artifacts and upstream package channels remain explicitly distinguished

#### Scenario: Public description differs from source documentation

- **WHEN** repository About, a release note or an image description contains an unsupported verification claim
- **THEN** the audit records the public discrepancy and its observation date
- **AND** a local documentation correction does not close that public discrepancy

### Requirement: Installation command examples identify shell and substitution boundaries

Installation command blocks MUST use syntax appropriate to their named shell and MUST separate PowerShell from Bash launchers. Required substitutions MUST be identified before execution and MUST NOT be expressed as unquoted shell redirections. Commands depending on a source checkout, installed executable, configured cluster or running process MUST state that prerequisite. Verification records MUST distinguish parsing, isolated execution, prior dated evidence and unexecuted commands; parser success alone MUST NOT be reported as a successful installation.

#### Scenario: Select a source revision in Bash or PowerShell

- **WHEN** an operator substitutes a selected full commit SHA into the named-shell source example
- **THEN** Git receives the revision as an argument without shell redirection
- **AND** a failed source selection prevents continuing the example

#### Scenario: Execute a Windows checkout launcher

- **WHEN** a Windows reader follows the checkout example
- **THEN** the launcher is in a PowerShell block with the checkout prerequisite
- **AND** the Bash block contains only the Bash launcher

## MODIFIED Requirements

### Requirement: README stays a quickstart

`README.md` SHALL remain a slim quickstart: hero screenshots, feature summary, Quick Start, a single in-README client configuration path (Codex CLI) with a table linking other clients to the docs site, configuration and data pointers, documentation links, and development notes. Detailed operational content (auth modes, routing guide, database runbooks, Kubernetes, remote setup, per-client walkthroughs) SHALL live on the documentation site instead. The README SHALL carry a prominent link to fork documentation; when the published fork site is stale or unverified, that link MUST select the tracked fork documentation source. The README SHALL keep the all-contributors generated block between its `ALL-CONTRIBUTORS-LIST` markers. `README.zh-CN.md` SHALL carry a banner identifying the English fork documentation as canonical.

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

#### Scenario: Published fork site is stale

- **WHEN** the published fork site has stale installation instructions or upstream edit links
- **THEN** the README directs operational readers to the tracked fork guides
- **AND** the audit records the separate public publication gap
