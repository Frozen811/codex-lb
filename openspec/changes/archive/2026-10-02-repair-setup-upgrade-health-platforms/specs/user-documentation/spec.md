## ADDED Requirements

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
