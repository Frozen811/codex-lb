## MODIFIED Requirements

### Requirement: Fork publication requires successful exact-source checks

The independent fork publisher SHALL require an explicit `vX.Y.Z` or `vX.Y.Z-(alpha|beta|rc).N` tag resolving to the current `main` commit. Before publication it MUST validate the newest main-push run for that exact SHA of CI, release guards, simplicity budgets and Windows startup regression; all four MUST be completed successfully and CI MUST contain a successful `CI Required` aggregate. Missing, pending, cancelled, skipped, failed, stale-SHA or pull-request-only evidence MUST block publication. The publisher MUST recheck source identity and CI after building and before registry login or artifact upload.

#### Scenario: Another SHA has green CI

- **WHEN** the tag's source CI failed but a different commit passed
- **THEN** publication is refused without registry login or artifact upload

#### Scenario: CI is rerun during artifact building

- **WHEN** the initial gate passed but the newest exact-source CI run is pending or failed at the final gate
- **THEN** no artifacts or Docker aliases are published

#### Scenario: Windows evidence is absent or unsuccessful

- **WHEN** the exact-source main-push Windows startup run is absent, pending or unsuccessful
- **THEN** fork publication is refused even if Linux CI passed
