## Why

DOC-INSTALL-01/02/03 identify installation entry points that still send fork users to upstream guides, mix shell syntax, or imply that historical artifacts contain current source fixes. Public repository metadata also contradicts the independent audit.

## What Changes

- Align fork descriptions and documentation links across entry points and deployment guides.
- Identify historical artifact provenance without replacing upstream references with nonexistent fork artifacts.
- Separate PowerShell and Bash examples, use shell-safe revision placeholders, and record executed command evidence and remaining external publication gaps.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `user-documentation`: installation links, shell examples and public metadata evidence contracts.

## Impact

README translations, COMMUNITY_RELEASE, rendered documentation, documentation regression coverage and issues-check. No application API, dependencies, settings, migrations or public publication changes.
