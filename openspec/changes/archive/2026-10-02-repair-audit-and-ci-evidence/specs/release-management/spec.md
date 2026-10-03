## ADDED Requirements

### Requirement: Upstream release automation has repository-scoped cleanup

Upstream release-please, beta synchronization, beta publishing and upstream artifact publishing SHALL run only in `Soju06/codex-lb`. The upstream Release workflow's failure cleanup MUST also be restricted to that repository. A skipped or cancelled upstream release workflow in a fork MUST NOT withdraw fork release metadata; fork publication SHALL remain governed by the independent fork publisher and its source gates.

#### Scenario: Upstream publisher is cancelled in a fork

- **WHEN** the upstream Release workflow receives a fork release event and an upstream publishing job is cancelled or skipped
- **THEN** upstream cleanup does not edit the fork release

#### Scenario: Upstream publication fails in upstream

- **WHEN** required upstream publishing fails or is cancelled after a public upstream release event
- **THEN** repository-scoped cleanup remains eligible to make that upstream release draft
