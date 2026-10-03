## MODIFIED Requirements

### Requirement: Docs pages link their governing OpenSpec capability

OpenSpec remains the normative source of truth. Every docs page that documents spec-governed behavior SHALL carry a link to the governing `openspec/specs/<capability>/` location in `Frozen811/codex-lb` on GitHub, and docs pages MUST NOT introduce requirements or behavior claims absent from OpenSpec. Generated pages MUST preserve this fork ownership when regenerated.

#### Scenario: Behavior page carries a spec link

- **WHEN** a reader opens a docs page describing spec-governed behavior (e.g. routing strategies)
- **THEN** the page contains a link to the governing capability under the fork's `openspec/specs/` on GitHub

#### Scenario: Settings reference is regenerated

- **WHEN** the generated settings reference is rebuilt
- **THEN** its owning-spec links still target the fork

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

## ADDED Requirements

### Requirement: Verification claims identify their evidence scope

Entry-point documentation and audit summaries MUST distinguish source-author resolution claims from independent verification. Quantitative inventories MUST identify their counting unit and source snapshot; linked issues, pull requests and discussions MUST NOT be presented as verified fixes or current open GitHub counts. Documentation MUST NOT claim all tracked defects are resolved or production readiness while the independent audit still has unverified items. Historical release names SHALL remain identifiable without implying that their artifacts contain later source fixes.

#### Scenario: Historical issue registry includes resolved markers

- **WHEN** the registry includes imported resolved markers without independent evidence for every entry
- **THEN** its summary labels them as source claims and points to the independent audit

#### Scenario: Source fixes postdate published artifacts

- **WHEN** entry-point docs reference a historical release
- **THEN** they identify that historical scope and do not advertise later source verification as proof of the release artifacts
