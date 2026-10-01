## Why

F-005 reports inconsistent quarantine deadlines in CI, F-011 breaks architecture diagnostics on Windows, and F-008 has no automated Windows startup evidence. Fix these three findings with regression coverage and distinguish local validation from published workflow results.

## What Changes

- Reproduce quarantine provenance failure and repair the cause without relaxing ownership or deadline assertions.
- Format architecture diagnostic paths consistently across operating systems.
- Run Windows portability tests and isolated package readiness smoke automatically, and require exact-source Windows success before fork publication.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `proxy-architecture`: portable diagnostic paths.
- `github-automation`: automatic Windows startup regression coverage.
- `release-management`: exact-source Windows workflow evidence before fork publication.

## Impact

Architecture checker, quarantine regression coverage (runtime scope determined by reproduction), Windows workflow, and fork release gate. No new configuration, dependency, schema or release version.
