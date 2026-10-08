## ADDED Requirements

### Requirement: Dashboard browser-smoke dependency installation is bounded

Dashboard browser-smoke CI MUST have an explicit job execution limit of at most twenty minutes and an explicit Chromium/dependency installation-step limit of at most ten minutes. APT dependency acquisition on the disposable Ubuntu runner MUST use finite HTTP and HTTPS connection/data timeouts of at most thirty seconds and no more than two acquisition retries. Cached Chromium MUST NOT bypass required operating-system dependency installation. An installation failure or deadline expiration MUST remain a failed browser-smoke outcome that prevents CI Required from passing.

#### Scenario: Package mirror stops responding

- **WHEN** an Ubuntu package mirror stops delivering dependency metadata or package data during browser setup
- **THEN** APT applies its finite acquisition timeout and bounded retries
- **AND** the installation step and browser-smoke job retain their explicit outer execution limits
- **AND** unsuccessful setup does not produce a successful CI Required result

#### Scenario: Browser cache is restored

- **WHEN** the job restores its pinned Chromium cache
- **THEN** operating-system dependency installation is still executed under the configured bounds
- **AND** the real dashboard browser tests remain mandatory for a successful browser-smoke result
