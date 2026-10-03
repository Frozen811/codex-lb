## ADDED Requirements

### Requirement: CI area detection includes complete change evidence

Pull-request CI SHALL select affected areas from every changed file, including both names of renamed files. If file evidence is unavailable, malformed, cyclic, or incomplete relative to the pull request's changed-file count, CI MUST select every area. Changes to CI selection or workflow definitions MUST select every area. Packaging hooks MUST trigger backend, Docker and Nix checks, and changes to Nix package source inputs MUST trigger Nix checks.

#### Scenario: Backend source is renamed outside backend

- **WHEN** a PR renames a file from `app/` into another area
- **THEN** backend CI runs for the removed source path as well as checks for the new path

#### Scenario: API returns only part of the change

- **WHEN** the PR reports more changed files than the API returns, or a page is malformed or repeats
- **THEN** all CI areas are selected without claiming the partial list is complete

#### Scenario: Packaging or selector changes

- **WHEN** a packaging hook or CI selector changes
- **THEN** packaging checks run for the hook, and all areas run for the selector

#### Scenario: Nix source changes

- **WHEN** application, frontend, configuration or build-helper inputs consumed by the Nix package change
- **THEN** Nix validation runs
