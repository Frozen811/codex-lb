## ADDED Requirements

### Requirement: Helm external installs progress before readiness waits

External database installs MUST retain a schema gate and run the install migration before Helm readiness waits can block it. Installs that need a chart-created or asynchronously materialized application Secret MUST create a regular migration Job with the application resources. Pre-install migration hooks MUST be used only when the application Secret already exists. Upgrades MUST retain pre-upgrade migration ordering. Bundled installs SHALL retain startup migration and upgrade-only migration Jobs.

#### Scenario: Direct URL with a generated encryption key

- **WHEN** an operator installs against a fresh external database using a direct URL and `--wait`
- **THEN** the migration Job can run alongside the chart-managed Secret
- **AND** the schema gate allows the application to become Ready after migration completes

#### Scenario: Existing database Secret without an application Secret

- **WHEN** the DB URL Secret already exists but the chart creates the application Secret
- **THEN** migration is a regular install Job and does not reference an unavailable pre-install encryption key

#### Scenario: External Secrets materialization

- **WHEN** the chart relies on External Secrets Operator to create application credentials
- **THEN** the install migration is a regular Job that can wait for those credentials without a post-install readiness cycle

#### Scenario: Existing application credentials and upgrades

- **WHEN** an application Secret already exists at install time or the release is upgraded
- **THEN** the chart retains the applicable pre-install or pre-upgrade migration hook

#### Scenario: Read-only container root filesystem

- **WHEN** the chart starts application pods with a read-only root filesystem
- **THEN** runtime metadata and scratch data use a writable mounted directory
- **AND** the shared encryption key remains explicitly mounted from its Secret

### Requirement: Fork Helm and Nix guidance identifies source and artifact channels

Helm image defaults and fork Nix quick-start commands MUST select Frozen811/codex-lb. Instructions MUST distinguish source checkout builds, pinned remote source and historical public artifacts. They MUST specify required install overlays, data/key retention and upgrade/rollback boundaries. Documentation MUST NOT assume an unshipped systemd unit exists.

#### Scenario: Install the local Helm chart

- **WHEN** an operator follows the fork Kubernetes guide
- **THEN** the chart and explicitly selected image come from the fork checkout
- **AND** the instructions name the installed StatefulSet when draining replicas

#### Scenario: Bundled PostgreSQL dependency identity

- **WHEN** an operator installs the bundled PostgreSQL overlay
- **THEN** the dependency image is pinned by immutable digest rather than a mutable latest tag

#### Scenario: Run the Nix package

- **WHEN** an operator follows the Nix quick start from a fork checkout
- **THEN** the package runs with dashboard assets and writable configured data outside the Nix store
- **AND** the guide identifies tested platforms separately from declared flake systems

### Requirement: Nix frontend installation does not depend on store hardlinks

Nix frontend builds MUST install locked dependencies without requiring a build user to hardlink root-owned immutable store files into the writable build directory.

#### Scenario: Protected hardlinks in a Linux build environment

- **WHEN** the build user's filesystem rejects hardlinks to immutable dependency files
- **THEN** the frontend dependency installation succeeds using a copying backend
- **AND** the installed package contains usable dashboard assets
