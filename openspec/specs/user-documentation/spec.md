# user-documentation Specification

## Purpose
Contracts for user-facing documentation: the published mkdocs-material site (strict builds, deploy from `main`, spec backlinks on behavior pages) and the entry-point documents — a README that stays a quickstart and a fully commented, zero-drift `.env.example` — so detailed material lives on the docs site instead of re-growing the README. OpenSpec remains the normative SSOT; docs pages render behavior, they do not define it.

## Requirements

### Requirement: Documentation site builds strictly and deploys from main

The repository SHALL contain a mkdocs-material documentation site (`mkdocs.yml` with `docs_dir: docs`). The fork site's repository and edit links MUST target `Frozen811/codex-lb`. Main deployment builds MUST use the configured GitHub Pages base URL; local and PR builds SHALL default to the fork's GitHub Pages URL. A dedicated GitHub Actions workflow SHALL build the site with `mkdocs build --strict` on every pull request that touches docs inputs and on pushes to `main`, and SHALL deploy to GitHub Pages only for non-pull-request events on `main`. The deploy job MUST use least-privilege permissions (`pages: write`, `id-token: write` scoped to the deploy job) and MUST NOT cancel in-flight deploys.

#### Scenario: PR with a broken internal docs link fails the build

- **GIVEN** a pull request editing a page under `docs/` with a link to a nonexistent page or anchor
- **WHEN** the Docs workflow runs
- **THEN** `mkdocs build --strict` fails the build check
- **AND** no Pages deploy is attempted for the pull request

#### Scenario: Push to main deploys the site

- **WHEN** a commit touching `docs/**` or `mkdocs.yml` lands on `main`
- **THEN** the workflow builds the site strictly, uploads the Pages artifact, and deploys it to the `github-pages` environment

#### Scenario: Fork page is edited or deployed to a custom endpoint

- **WHEN** a fork page is rendered for a main deployment
- **THEN** its edit link targets the fork and its canonical URL uses the configured Pages base URL

### Requirement: Docs pages link their governing OpenSpec capability

OpenSpec remains the normative source of truth. Every docs page that documents spec-governed behavior SHALL carry a link to the governing `openspec/specs/<capability>/` location in `Frozen811/codex-lb` on GitHub, and docs pages MUST NOT introduce requirements or behavior claims absent from OpenSpec. Generated pages MUST preserve this fork ownership when regenerated.

#### Scenario: Behavior page carries a spec link

- **WHEN** a reader opens a docs page describing spec-governed behavior (e.g. routing strategies)
- **THEN** the page contains a link to the governing capability under the fork's `openspec/specs/` on GitHub

#### Scenario: Settings reference is regenerated

- **WHEN** the generated settings reference is rebuilt
- **THEN** its owning-spec links still target the fork

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

### Requirement: .env.example is a commented zero-drift sample

`.env.example` SHALL contain only commented-out values, SHALL NOT state values that contradict the code defaults in `app/core/config/settings.py`, and SHALL retain the commented `# CODEX_LB_LEADER_ELECTION_ENABLED=false` single-instance escape hatch. Copying the file verbatim MUST yield the same behavior as running with no configuration.

#### Scenario: Copying the sample changes nothing

- **GIVEN** a fresh install
- **WHEN** the operator copies `.env.example` to `.env.local` without uncommenting anything
- **THEN** the application starts with identical effective settings to a no-.env install
- **AND** leader election remains enabled

#### Scenario: Leader-election escape hatch stays documented

- **WHEN** `.env.example` is read
- **THEN** it contains the commented line `# CODEX_LB_LEADER_ELECTION_ENABLED=false`
- **AND** no active (uncommented) assignment disables leader election

### Requirement: Generated settings reference stays in sync with the code

The documentation site SHALL include a settings reference page
(`docs/reference/settings.md`) generated from `Settings.model_fields` by
`scripts/generate_settings_reference.py`. The page SHALL list, for every
setting, its environment variable name — the `CODEX_LB_`-prefixed name, or,
for a setting declared with explicit validation aliases, the primary alias
followed by the remaining aliases — its type, and its default
(environment-derived defaults rendered symbolically), grouped by functional
area; it SHALL document the bare `PORT` special case, the
`CODEX_LB_ENV_FILE` bootstrap variable, and the `CODEX_LB_WORKERS_PER_INSTANCE`
startup guard (which is not a setting), SHALL list the process-level
environment variables codex-lb honors without making them settings
(third-party or POSIX conventions read by the launcher, libraries, or frozen
migrations), and SHALL list the removed (`_REMOVED_SETTINGS`) env names
sourced from the code. The generated page SHALL be
checked into the repository so the strict docs build stays hermetic, SHALL
carry a header identifying it as generated, and SHALL link the owning
OpenSpec capability. CI unit tests MUST fail when the checked-in page differs
from regenerated output, when the settings surface exceeds its ratchet
(lower-only without a simplicity-budget decision), or when an uncommented
`.env.example` assignment differs from the code default.

#### Scenario: Settings change without regeneration fails CI
- **GIVEN** a change to `Settings` fields in `app/core/config/settings.py`
- **WHEN** the unit test suite runs without regenerating `docs/reference/settings.md`
- **THEN** the regenerate-and-diff test fails until the page is regenerated and committed

#### Scenario: Reference page is reachable and generated
- **WHEN** a reader opens the published settings reference page
- **THEN** it is in the site navigation and linked from the Configuration page
- **AND** it identifies itself as generated from `scripts/generate_settings_reference.py`
- **AND** it links the owning OpenSpec capability

#### Scenario: Settings surface growth trips the ratchet
- **WHEN** the number of `Settings` fields exceeds the ratchet value
- **THEN** the ratchet unit test fails, forcing a simplicity-budget discussion before the surface grows

#### Scenario: Aliased setting renders every env name
- **WHEN** a setting is declared with validation aliases (for example `forwarded_allow_ips`)
- **THEN** the reference row shows the primary env name and each alias
- **AND** an operator can find the setting by either name

#### Scenario: Process-level conventions are documented but not settings
- **WHEN** codex-lb honors an environment variable that is a third-party or POSIX convention
- **THEN** the reference lists it in the process-level section with its consumer
- **AND** it is not counted toward the settings ratchet

#### Scenario: Removed names are listed without a deprecated-alias section

- **WHEN** the reference page is regenerated
- **THEN** its "Removed" section lists exactly the names in `_REMOVED_SETTINGS`
- **AND** the page has no deprecated-env-alias list

### Requirement: Client examples recommend current frontier model lineup

Client setup documentation across the quickstart README and the documentation site SHALL recommend `gpt-6-astra` for complex reasoning and coding tasks. Model-specific context-window guides (such as the 872k context-window opt-in) SHALL remain specific to the GPT-5.6 family. Inert client configuration profiles and multi-client configuration examples SHALL demonstrate current frontier defaults without modifying catalog, pricing, or protocol contracts.

#### Scenario: Client setup examples use GPT-6 Astra

- **WHEN** an operator inspects the quickstart client setup section in `README.md`, `README.zh-CN.md`, or `docs/client-setup.md`
- **THEN** the primary model configuration snippet uses `gpt-6-astra` with `model_reasoning_effort = "xhigh"`

#### Scenario: GPT-5.6 context-window opt-in instructions remain family-specific

- **WHEN** an operator reviews large context-window instructions
- **THEN** the 872k context-window opt-in instructions explicitly apply to the `gpt-5.6-*` family

### Requirement: Verification claims identify their evidence scope

Entry-point documentation and audit summaries MUST distinguish source-author resolution claims from independent verification. Quantitative inventories MUST identify their counting unit and source snapshot; linked issues, pull requests and discussions MUST NOT be presented as verified fixes or current open GitHub counts. Documentation MUST NOT claim all tracked defects are resolved or production readiness while the independent audit still has unverified items. Historical release names SHALL remain identifiable without implying that their artifacts contain later source fixes.

#### Scenario: Historical issue registry includes resolved markers

- **WHEN** the registry includes imported resolved markers without independent evidence for every entry
- **THEN** its summary labels them as source claims and points to the independent audit

#### Scenario: Source fixes postdate published artifacts

- **WHEN** entry-point docs reference a historical release
- **THEN** they identify that historical scope and do not advertise later source verification as proof of the release artifacts

### Requirement: Client setup identifies authentication and endpoint contracts

Client setup documentation MUST distinguish a Codex LB API key from dashboard credentials and upstream ChatGPT credentials. It MUST identify generation-provider, catalog and usage base URL suffixes consistently across the guide and shipped examples, and label the tested client version and synthetic versus live upstream evidence. Client instructions MUST NOT contain merge-conflict markers or promise conversation synchronization from provider identity alone.

#### Scenario: Configure an API-key Codex CLI provider

- **WHEN** an operator configures a key-authenticated Codex CLI provider
- **THEN** the guide identifies the key environment and provider's selected auth mode
- **AND** generation, catalog and usage URLs refer to the selected deployment with their required suffixes

### Requirement: Setup failure diagnostics distinguish infrastructure and product signals

Troubleshooting guidance MUST distinguish startup, liveness and infrastructure readiness from dashboard assets, native-helper transport and authenticated upstream operation. It MUST identify observable failure stages and recovery for invalid environment, unavailable DB, missing dashboard assets/helper, occupied HTTP port, upstream failure and process shutdown, without publishing secrets or changing mandatory auth/verification. It MUST state that optional helper absence and upstream degradation do not automatically imply infrastructure unreadiness.

#### Scenario: Ready backend has no dashboard or upstream

- **WHEN** readiness succeeds but dashboard assets are absent or upstream requests fail
- **THEN** the guidance tests those product paths separately and identifies their distinct recovery

### Requirement: Installation platform claims identify executed evidence

Installation guidance MUST provide a platform/topology evidence matrix that separates executed runtime checks, declared build targets and unexecuted configurations. Runtime manifests MUST be distinguished from attestations; an unknown/unknown entry MUST NOT be presented as ARM64 support. Python package portability and flake target declarations MUST NOT be represented as verification of every native OS/architecture. Evidence MUST name its source/artifact/date and preserve unexecuted platform boundaries.

#### Scenario: Artifact declares additional architectures

- **WHEN** a release index or build configuration includes attestations or declared systems without runtime verification
- **THEN** the guide records only the observed runtime platform as verified
- **AND** leaves other systems explicitly unexecuted

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
